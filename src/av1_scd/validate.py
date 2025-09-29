from av1_scd import predefined, log
import shutil


def validate_pg_lib(scd_method: str):
    use_ffmpeg = scd_method in predefined.USE_FFMPEG_METHOD
    if use_ffmpeg:
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path is None:
            log.error_log("ffmpeg is missing. install and add it to PATH")

    if scd_method == predefined.ALL_SCD_METHOD[2]:
        av_scene_path = shutil.which("av-scenechange")
        if av_scene_path is None:
            log.error_log("av-scenechange is missing. install and add it to PATH")
