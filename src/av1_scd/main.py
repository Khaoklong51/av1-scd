import os
from av1_scd import option, mediainfo, keyframes, cfg, log


input_file = option.input_file
output_file = option.output_file
scd_method = option.scd_method
enc_format = option.enc_format
ALL_SCD_METHOD = option.ALL_SCD_METHOD
ALL_CFG_OPT = option.ALL_CFG_OPT
is_print = option.is_print


def get_print_final() -> str:
    final_help = ""
    if enc_format == ALL_CFG_OPT[0]:  # x264
        final_help = (
            f"Feed the config file to {enc_format} using --qpfile "
            "with '--keyint infinite --no-scenecut' option"
        )
    elif enc_format == ALL_CFG_OPT[1]:  # x265
        final_help = (
            f"Feed the config file to {enc_format} using --qpfile "
            "with '--keyint -1 --no-scenecut' option"
        )
    elif enc_format == ALL_CFG_OPT[2]:  # svt-av1
        final_help = (
            "Feed the config file to SvtAv1EncApp using -c or --config "
            "with --keyint -1 option"
        )
    elif (
        enc_format == ALL_CFG_OPT[3] or enc_format == ALL_CFG_OPT[4]
    ):  # av1an and av1an-git
        final_help = "Feed the scene file to av1an using -s or --scenes option"
    elif enc_format == ALL_CFG_OPT[5]:  # ffmpeg
        final_help = (
            "Feed the content of config file to -force_key_frames:v option "
            "in ffmpeg also make sure to disable keyframe placement "
            "with the encoder you use"
        )

    return final_help


def main():
    option.validate_lib()
    track_data = mediainfo.get_pymediainfo_data(input_file)
    log.info_log("Get mediainfo data")
    # if user does not specify min or max scene use 5 sec framerate
    if option.min_scene_len == -2:
        option.min_scene_len, _ = mediainfo.get_scene_len(track_data)
    if option.max_scene_len == -2:
        _, option.max_scene_len = mediainfo.get_scene_len(track_data)
    log.info_log(f"Min scene len {option.min_scene_len}")
    log.info_log(f"Max scene len {option.max_scene_len}")
    keyframe_list = []
    # already validata library
    if scd_method == ALL_SCD_METHOD[0]:
        from av1_scd.scd import pyscene

        log.info_log(f"Use scene method '{ALL_SCD_METHOD[0]}'")
        keyframe_list = pyscene.get_keyframe_pyscene(input_file)
    elif scd_method == ALL_SCD_METHOD[1]:
        from av1_scd.scd import vsxvid

        log.info_log(f"Use scene method '{ALL_SCD_METHOD[1]}'")
        vid_height = mediainfo.get_vid_height(track_data)
        keyframe_list = vsxvid.get_keyframe_vsxvid(input_file, vid_height)
    elif scd_method == ALL_SCD_METHOD[2]:
        from av1_scd.scd import avscenechange

        log.info_log(f"Use scene method '{ALL_SCD_METHOD[2]}'")
        pix_fmt = mediainfo.get_ffmpeg_pixfmt(track_data)
        keyframe_list = avscenechange.get_keyframe_avscenechange(
            input_file, pix_fmt, mediainfo.get_frame_count(track_data)
        )

    keyframe_list = keyframes.process_keyframe(
        keyframe_list, mediainfo.get_frame_count(track_data)
    )
    log.debug_log(f"Keyframe list {str(keyframe_list)}")

    log.info_log(f"Keyframes Config '{enc_format.lower()}'")
    enc_data = ""
    if enc_format == ALL_CFG_OPT[0]:  # x264
        enc_data = cfg.get_scene_x264(keyframe_list)
    elif enc_format == ALL_CFG_OPT[1]:  # x265
        enc_data = cfg.get_scene_x265(keyframe_list)
    elif enc_format == ALL_CFG_OPT[2]:  # svt-av1
        enc_data = cfg.get_scene_svtapp(keyframe_list)
    elif enc_format == ALL_CFG_OPT[3]:  # av1an
        enc_data = cfg.get_scene_av1an(keyframe_list)
    elif enc_format == ALL_CFG_OPT[4]:  # av1an-git
        enc_data = cfg.get_scene_av1an_git(keyframe_list)
    elif enc_format == ALL_CFG_OPT[5]:  # ffmpeg
        enc_data = cfg.get_scene_ffmpeg(keyframe_list)

    log.debug_log(f"Create folder at {os.path.dirname(output_file)}")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    log.debug_log(f"Write file to {output_file}")
    with open(output_file, mode="w", encoding="utf-8") as f:
        f.write(enc_data)

    if is_print:
        print(enc_data)
    else:
        print(get_print_final())
