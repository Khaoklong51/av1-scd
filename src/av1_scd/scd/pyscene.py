import scenedetect as sc
from av1_scd import log, predefined
from pathlib import Path
from av1_scd import option as opt


def get_keyframe_pyscene(input_path: Path) -> list:
    video: sc.VideoStream = sc.open_video(str(input_path), backend=opt.pysc_decode)
    local_threshold = opt.threshold
    if local_threshold == -2:
        local_threshold = predefined.THRESHOLD[f"pysc-{opt.pysc_method}"]
    log.info_log(f"Select treshold {local_threshold}")
    scene_manager: sc.SceneManager = sc.SceneManager()
    if opt.pysc_method == predefined.ALL_PYSC_METHOD[0]:  # adaptive
        scene_manager.add_detector(
            sc.AdaptiveDetector(
                min_scene_len=opt.min_scene_len, adaptive_threshold=local_threshold
            )
        )
    elif opt.pysc_method == predefined.ALL_PYSC_METHOD[1]:  # content
        scene_manager.add_detector(
            sc.ContentDetector(min_scene_len=opt.min_scene_len, threshold=local_threshold)
        )
    elif opt.pysc_method == predefined.ALL_PYSC_METHOD[2]:  # threshold
        scene_manager.add_detector(
            sc.ThresholdDetector(
                min_scene_len=opt.min_scene_len, threshold=local_threshold
            )
        )
    elif opt.pysc_method == predefined.ALL_PYSC_METHOD[3]:  # hash
        scene_manager.add_detector(
            sc.HashDetector(min_scene_len=opt.min_scene_len, threshold=local_threshold)
        )
    elif opt.pysc_method == predefined.ALL_PYSC_METHOD[4]:  # histogram
        scene_manager.add_detector(
            sc.HistogramDetector(
                min_scene_len=opt.min_scene_len, threshold=local_threshold
            )
        )

    log.info_log(f"Pyscene method {opt.pysc_method}")

    log.info_log(f"Pyscene downscale {opt.pysc_down_factor}")
    if isinstance(opt.pysc_down_factor, int):
        scene_manager.downscale = opt.pysc_down_factor
        scene_manager.auto_downscale = False
    elif isinstance(opt.pysc_down_factor, str) and opt.pysc_down_factor == "auto":
        scene_manager.auto_downscale = True

    scene_manager.detect_scenes(video=video, show_progress=True)

    scene_list = scene_manager.get_scene_list(start_in_scene=True)

    keyframes_cut: list[int] = []

    for scene in scene_list:
        keyframes_cut.append(scene[0].get_frames())

    # add last frame
    keyframes_cut.append(scene_list[-1][1].get_frames())

    return keyframes_cut
