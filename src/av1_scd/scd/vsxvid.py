from av1_scd import predefined
import vapoursynth as vs
import vstools
from av1_scd import log
from pathlib import Path
from av1_scd import option as opt

core = vs.core


def _check_vs_source():
    vs_source = {"bestsource": False, "ffms2": False, "lsmash": False}

    if hasattr(core, "bs"):
        vs_source["bestsource"] = True
    if hasattr(core, "ffms2"):
        vs_source["ffms2"] = True
    if hasattr(core, "lsmas"):
        vs_source["lsmash"] = True

    if opt.vs_source == predefined.ALL_VS_SOURCE[0] and not vs_source["bestsource"]:
        log.error_log(
            "bestsource is unavailable. Install https://github.com/vapoursynth/bestsource"
        )
    elif opt.vs_source == predefined.ALL_VS_SOURCE[1] and not vs_source["ffms2"]:
        log.error_log("ffms2 is unavailable. Install https://github.com/FFMS/ffms2")
    elif opt.vs_source == predefined.ALL_VS_SOURCE[2] and not vs_source["lsmash"]:
        log.error_log(
            "lsmash is unavailable. Install https://github.com/HomeOfAviSynthPlusEvolution/L-SMASH-Works"
        )


def _prepare_video(input_path: str):
    video = None
    if opt.vs_source == predefined.ALL_VS_SOURCE[0]:  # bestsource
        video = core.bs.VideoSource(input_path)
    elif opt.vs_source == predefined.ALL_VS_SOURCE[1]:  # ffms2
        video = core.ffms2.Source(input_path)
    elif opt.vs_source == predefined.ALL_VS_SOURCE[2]:  # lsmash
        video = core.lsmas.LibavSMASHSource(input_path)
    if video is None:
        log.error_log(f"Failed to use {opt.vs_source} source")

    return video


def get_keyframe_vsxvid(input_path: Path, vid_height: int) -> list:
    _check_vs_source()
    clip = _prepare_video(str(input_path))
    log.debug_log(f"Video height for vsxvid {vid_height}")
    keyframes = vstools.Keyframes.from_clip(clip, 0, height=vid_height)

    return [fr for fr in keyframes]
