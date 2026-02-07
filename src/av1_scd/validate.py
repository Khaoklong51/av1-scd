import importlib.util
from av1_scd import predefined, log
from av1_scd import option as opt
import shutil
import importlib


def validate_pg_lib():
    use_ffmpeg = opt.scd_method in predefined.USE_FFMPEG_METHOD
    if use_ffmpeg:
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path is None:
            log.error_log("ffmpeg is missing. install and add it to PATH")

    if opt.scd_method == predefined.ALL_SCD_METHOD[2]:
        av_scene_path = shutil.which("av-scenechange")
        if av_scene_path is None:
            log.error_log("av-scenechange is missing. install and add it to PATH")
        if opt.avsc_score_mode == predefined.ALL_AVSC_SCORE_MODE[1]:  # xav score mode
            log.info_log("Select Python binding for xav score mode")
            opt.avsc_mode = predefined.ALL_AVSC_MODE[1]  # pyav_scenechange
        if opt.avsc_mode == predefined.ALL_AVSC_MODE[1]:  # pyav_scenechange
            is_pyav_exist = importlib.util.find_spec("pyav_scenechange")
            if is_pyav_exist is None:
                log.error_log("No module named pyav_scenechange")
