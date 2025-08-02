import scenedetect as sc
from .. import option
from .. import log


min_kf_dist: int = option.min_scene_len
pysc_decode: str = option.pysc_decode
pysc_method: str = option.pysc_method
ALL_PYSC_METHOD = option._VALID_METHOD2
pysc_down_factor: str | int = option.pysc_down_factor


def get_keyframe_pyscene(input_path: str) -> list:
    video: sc.VideoStream = sc.open_video(input_path, backend=pysc_decode)
    scene_manager: sc.SceneManager = sc.SceneManager()
    if pysc_method == ALL_PYSC_METHOD[0]:  # adaptive
        scene_manager.add_detector(sc.AdaptiveDetector(min_scene_len=min_kf_dist))
    elif pysc_method == ALL_PYSC_METHOD[1]:  # content
        scene_manager.add_detector(sc.ContentDetector(min_scene_len=min_kf_dist))
    elif pysc_method == ALL_PYSC_METHOD[2]:  # threshold
        scene_manager.add_detector(sc.ThresholdDetector(min_scene_len=min_kf_dist))
    elif pysc_method == ALL_PYSC_METHOD[3]:  # hash
        scene_manager.add_detector(sc.HashDetector(min_scene_len=min_kf_dist))
    elif pysc_method == ALL_PYSC_METHOD[4]:  # histogram
        scene_manager.add_detector(sc.HistogramDetector(min_scene_len=min_kf_dist))

    log.info_log(f"Pyscene method '{pysc_method}'")

    if isinstance(pysc_down_factor, int):
        scene_manager.downscale = pysc_down_factor
    elif isinstance(pysc_down_factor, str) and pysc_down_factor == "auto":
        scene_manager.auto_downscale = True

    scene_manager.detect_scenes(video=video, show_progress=True)

    scene_list = scene_manager.get_scene_list(start_in_scene=True)

    keyframes_cut: list[int] = []

    for scene in scene_list:
        keyframes_cut.append(scene[0].get_frames())

    # add last frame
    keyframes_cut.append(scene_list[-1][1].get_frames())

    return keyframes_cut
