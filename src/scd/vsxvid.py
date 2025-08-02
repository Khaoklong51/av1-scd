from .. import option
import vapoursynth as vs
import vstools
from .. import log


min_kf_dist = option.min_scene_len
ALL_SOURCE_METHOD = option._VALID_METHOD4
vs_decode = option.vs_source
core = vs.core


def _check_vs_source():
    vs_source = {"bestsource": False, "ffms2": False, "lsmash": False}

    if hasattr(core, "bs"):
        vs_source["bestsource"] = True
    if hasattr(core, "ffms2"):
        vs_source["ffms2"] = True
    if hasattr(core, "lsmas"):
        vs_source["lsmash"] = True

    if vs_decode == ALL_SOURCE_METHOD[0] and not vs_source["bestsource"]:
        log.error_log(
            "bestsource is unavailable. Install https://github.com/vapoursynth/bestsource"
        )
    if vs_decode == ALL_SOURCE_METHOD[1] and not vs_source["ffms2"]:
        log.error_log("ffms2 is unavailable. Install https://github.com/FFMS/ffms2")
    if vs_decode == ALL_SOURCE_METHOD[2] and not vs_source["lsmash"]:
        log.error_log(
            "lsmash is unavailable. Install https://github.com/HomeOfAviSynthPlusEvolution/L-SMASH-Works"
        )


def _prepare_video(input_path: str):
    video = None
    if vs_decode == ALL_SOURCE_METHOD[0]:  # bestsource
        video = core.bs.VideoSource(input_path)
    elif vs_decode == ALL_SOURCE_METHOD[1]:  # ffms2
        video = core.ffms2.Source(input_path)
    elif vs_decode == ALL_SOURCE_METHOD[2]:  # lsmash
        video = core.lsmas.LibavSMASHSource(input_path)
    if video is None:
        log.error_log(f"Failed to use {vs_decode} source")

    return video


def get_keyframe_vsxvid(input_path: str, vid_height: int) -> list:
    _check_vs_source()
    clip = _prepare_video(input_path)
    keyframes = vstools.Keyframes.from_clip(clip, 0, height=vid_height)

    frames = [fr for fr in keyframes]
    return frames
