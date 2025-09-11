import cv2
import numpy as np
import tqdm
import onnxruntime as ort
from av1_scd import option, predefined, log
from pathlib import Path

min_scene_len = option.min_scene_len
max_scene_len = option.max_scene_len
threshold = option.treshold
model_path = option.transnet_model_path
gpu_providers = predefined.GPU_PROVIDER


def _extract_frames_opencv(input_path: Path, frame_count: int, target_size=(48, 27)):
    cap = cv2.VideoCapture(str(input_path))
    frames = []

    with tqdm.tqdm(total=frame_count, desc="Extracting frames") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Resize frame to (width=48, height=27)
            frame_resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
            pbar.update(1)

        pbar.n = frame_count
        pbar.refresh()
        pbar.close()

    cap.release()
    frames_np = np.array(frames, dtype=np.float32)
    return frames_np


def _is_gpu_available():
    """Checks if CUDA or other GPU providers are available for ONNX Runtime"""
    providers = ort.get_available_providers()
    return any(p in providers for p in gpu_providers)


def _predictions_to_scenes(
    predictions: np.ndarray,
    soft_predictions: np.ndarray,
    total_frames: int,
) -> list[tuple[int, int]]:
    """
    Convert TransNet predictions into scene boundaries,
    avoiding cuts inside fades and respecting min/max scene lengths.

    Returns: list of (start_frame, end_frame) tuples.
    """
    # defined hard code variable
    fade_threshold_low: float = 0.05
    fade_threshold_high: float = 1.0
    min_fade_len: int = min_scene_len // 3
    merge_gap_between_fades: int = min_scene_len // 6
    local_threshold = threshold
    if local_threshold == -2:
        local_threshold = predefined.THRESHOLD["transnetv2"]

    def smart_split_scene(start: int, end: int) -> list[tuple[int, int]]:
        """Split a long scene intelligently based on predictions."""
        result = []
        cur_start = start

        while end - cur_start > max_scene_len:
            ideal_split = cur_start + max_scene_len
            search_start = max(cur_start + min_scene_len, ideal_split - min_scene_len)
            search_end = min(end - min_scene_len, ideal_split + min_scene_len)

            if search_start >= search_end:
                split_at = ideal_split  # fallback
            else:
                split_at = max(
                    range(search_start, search_end + 1), key=lambda f: predictions[f]
                )

            result.append((cur_start, split_at))
            cur_start = split_at

        result.append((cur_start, end))
        return result

    hard_cuts = np.where(predictions > threshold)[0] + 1

    # Detect fade segments
    is_fade_frame = (soft_predictions >= fade_threshold_low) & (
        soft_predictions <= fade_threshold_high
    )
    fade_segments = []
    in_fade = False
    start_fade = 0

    for i, is_fade in enumerate(is_fade_frame):
        if is_fade and not in_fade:
            in_fade = True
            start_fade = i
        elif not is_fade and in_fade:
            if i - start_fade >= min_fade_len:
                fade_segments.append([start_fade, i])  # inclusive start, exclusive end
            in_fade = False

    if in_fade and (total_frames - start_fade >= min_fade_len):
        fade_segments.append([start_fade, total_frames])  # inclusive start, exclusive end

    # Merge close fades
    merged_fades = []
    for seg in fade_segments:
        if not merged_fades:
            merged_fades.append(seg)
        else:
            prev = merged_fades[-1]
            if seg[0] - prev[1] <= merge_gap_between_fades:
                merged_fades[-1][1] = seg[1]
            else:
                merged_fades.append(seg)

    # Adjust hard cuts overlapping fades
    adjusted_cuts = set()
    for cut in hard_cuts:
        for fade_start, fade_end in merged_fades:
            if fade_start <= cut <= fade_end:
                candidate = fade_end  # already exclusive
                if candidate - fade_start >= min_scene_len:
                    adjusted_cuts.add(candidate)
                else:
                    adjusted_cuts.add(fade_start)  # fallback to fade start
                break
        else:
            adjusted_cuts.add(cut)

    all_cuts = adjusted_cuts | {0, total_frames}  # total_frames = exclusive end
    all_cuts = sorted(all_cuts)

    # Initial scene list (no splitting yet)
    initial_scenes = [(all_cuts[i], all_cuts[i + 1]) for i in range(len(all_cuts) - 1)]

    # Merge too-short scenes
    merged_scenes = []
    idx = 0
    while idx < len(initial_scenes):
        start, end = initial_scenes[idx]
        if end - start < min_scene_len:
            if merged_scenes:
                # merge into previous
                prev_start, prev_end = merged_scenes.pop()
                merged_scenes.append((prev_start, end))
            elif idx + 1 < len(initial_scenes):
                # merge into next
                next_start, next_end = initial_scenes[idx + 1]
                initial_scenes[idx + 1] = (start, next_end)
            else:
                # last fragment
                merged_scenes.append((start, end))
            idx += 1
        else:
            merged_scenes.append((start, end))
            idx += 1

    # Apply max_scene_len splitting
    split_scenes = []
    for start, end in merged_scenes:
        if end - start > max_scene_len:
            split_scenes.extend(smart_split_scene(start, end))
        else:
            split_scenes.append((start, end))

    return split_scenes


def transnet_scenes(
    opencv_frame: np.ndarray,
    total_frames: int,
):

    # Pad and batch into overlapping windows
    pad_start = np.repeat(opencv_frame[0:1], 25, axis=0)
    pad_end = np.repeat(opencv_frame[-1:], 25 + (50 - (total_frames % 50 or 50)), axis=0)
    padded_frames = np.concatenate([pad_start, opencv_frame, pad_end], axis=0)

    # Initialize ONNX Runtime session
    sess_options = ort.SessionOptions()
    backends = ort.get_available_providers()

    gpu_priority = [
        "MIGraphXExecutionProvider",
        "CUDAExecutionProvider",
        "DirectMLExecutionProvider",
        "ROCMExecutionProvider",
    ]

    if _is_gpu_available():
        for p in gpu_priority:
            if p in backends:
                providers = [p, "CPUExecutionProvider"]
                break
        else:
            providers = ["CPUExecutionProvider"]
    else:
        providers = ["CPUExecutionProvider"]

    log.debug_log(f"onnx provider {providers}")

    sess = ort.InferenceSession(
        str(model_path), sess_options=sess_options, providers=providers
    )
    input_name = sess.get_inputs()[0].name
    output_names = [output.name for output in sess.get_outputs()]

    ptr = 0
    batch_size = 50
    window_size = 100
    stride = 50
    predictions = []
    soft_predictions = []

    with tqdm.tqdm(total=total_frames, desc="Inferring scenes") as pbar:
        while ptr + window_size <= len(padded_frames):
            window = padded_frames[ptr : ptr + window_size][np.newaxis].astype(np.float32)
            logits, many_hot = sess.run(output_names, {input_name: window})

            single_frame_pred = logits[0, 25:75, 0]  # type: ignore
            all_frames_pred = many_hot[0, 25:75, 0]  # type: ignore

            predictions.append(single_frame_pred)
            soft_predictions.append(all_frames_pred)

            frames_done = min(batch_size, total_frames - (ptr // stride) * stride)
            pbar.update(frames_done)
            ptr += stride

    predictions = np.concatenate(predictions)[:total_frames]
    soft_predictions = np.concatenate(soft_predictions)[:total_frames]

    scenes_list = _predictions_to_scenes(predictions, soft_predictions, total_frames)

    return scenes_list


def get_keyframe_transnet(input_file: Path, frame_count: int) -> list[int]:
    log.warning_log("Transnetv2 is an experimental method")
    if model_path is None:
        log.error_log(
            "Transnet model not provided. provide model using --transnet-model option"
        )
    opencv_frame = _extract_frames_opencv(input_file, frame_count)
    scene_list = transnet_scenes(opencv_frame, frame_count)
    log.debug_log(f"Transnet Raw keyframe {scene_list}")

    keyframes = [start for start, _ in scene_list]

    return keyframes
