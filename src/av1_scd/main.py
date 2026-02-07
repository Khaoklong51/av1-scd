from av1_scd import mediainfo, keyframes, cfg, log, predefined, validate
from av1_scd import option as opt


def get_print_final() -> str:
    final_help = ""
    if opt.enc_format == predefined.ALL_CFG_OPT[0]:  # x264
        final_help = (
            "Feed the config file to x264 using --qpfile "
            "with '--keyint infinite --no-scenecut' option"
        )
    elif opt.enc_format == predefined.ALL_CFG_OPT[1]:  # x265
        final_help = (
            "Feed the config file to x265 using --qpfile "
            "with '--keyint -1 --no-scenecut' option"
        )
    elif opt.enc_format == predefined.ALL_CFG_OPT[2]:  # svt-av1
        final_help = (
            "Feed the config file to SvtAv1EncApp using -c or --config "
            "with --keyint -1 option"
        )
    elif opt.enc_format == predefined.ALL_CFG_OPT[3]:  # av1an
        final_help = "Feed the scene file to av1an using -s or --scenes option"
    elif opt.enc_format == predefined.ALL_CFG_OPT[4]:  # ffmpeg
        final_help = (
            "Feed the content of config file to -force_key_frames:v option "
            "in ffmpeg also make sure to disable keyframe placement "
            "with the encoder you use"
        )
    elif opt.enc_format == predefined.ALL_CFG_OPT[5]:  # xav
        final_help = "Feed the scene file to xav using -s or --sc option"

    return final_help


def main():
    validate.validate_pg_lib()
    log.info_log("Get mediainfo data")
    track_data = mediainfo.get_pymediainfo_data(opt.input_file)
    # if user does not specify min or max scene use 10 sec framerate
    if opt.min_scene_len == -2:
        opt.min_scene_len, _ = mediainfo.get_scene_len(track_data)
    if opt.max_scene_len == -2:
        _, opt.max_scene_len = mediainfo.get_scene_len(track_data)
    frame_count = mediainfo.get_frame_count(track_data)
    if opt.enc_format == predefined.ALL_CFG_OPT[5]:
        opt.min_scene_len, opt.max_scene_len = mediainfo.force_xav_len(track_data)
        log.warning_log(
            f"xav format select force min and max keyframe to {opt.min_scene_len} and {opt.max_scene_len}"
        )
    log.info_log(f"Min scene len {opt.min_scene_len}")
    log.info_log(f"Max scene len {opt.max_scene_len}")
    keyframe_list = []
    # already validata library
    if opt.scd_method == predefined.ALL_SCD_METHOD[0]:
        from av1_scd.scd import pyscene

        log.info_log(f"Use scene method {predefined.ALL_SCD_METHOD[0]}")
        keyframe_list = pyscene.get_keyframe_pyscene(opt.input_file)
    elif opt.scd_method == predefined.ALL_SCD_METHOD[1]:
        from av1_scd.scd import vsxvid

        log.info_log(f"Use scene method {predefined.ALL_SCD_METHOD[1]}")
        vid_height = 360  # default function
        if opt.vsxvid_height is None:
            vid_height = mediainfo.get_vid_height(track_data)
        else:
            vid_height = opt.vsxvid_height
        keyframe_list = vsxvid.get_keyframe_vsxvid(opt.input_file, vid_height)
    elif opt.scd_method == predefined.ALL_SCD_METHOD[2]:
        from av1_scd.scd import avscenechange

        log.info_log(f"Use scene method {predefined.ALL_SCD_METHOD[2]}")
        pix_fmt = mediainfo.get_ffmpeg_pixfmt(track_data)
        keyframe_list = avscenechange.get_keyframe_avscenechange(
            opt.input_file, pix_fmt, frame_count
        )
    elif (
        opt.scd_method == predefined.ALL_SCD_METHOD[3]
        or opt.scd_method == predefined.ALL_SCD_METHOD[4]
    ):
        from av1_scd.scd import ffmpeg
        from av1_scd import util

        if opt.scd_method == predefined.ALL_SCD_METHOD[3]:
            log.info_log(f"Use scene method {predefined.ALL_SCD_METHOD[3]}")
            keyframe_list = ffmpeg.get_keyframe_ffmpeg_scene(opt.input_file)
        elif opt.scd_method == predefined.ALL_SCD_METHOD[4]:
            log.info_log(f"Use scene method {predefined.ALL_SCD_METHOD[4]}")
            keyframe_list = ffmpeg.get_keyframe_ffmpeg_scdet(opt.input_file, frame_count)

        frame_rate = mediainfo.get_framerate(track_data)
        keyframe_list = util.frame_time_to_num(keyframe_list, frame_rate)
    elif opt.scd_method == predefined.ALL_SCD_METHOD[5]:
        from av1_scd.scd import transnetv2

        log.info_log(f"Use scene method {predefined.ALL_SCD_METHOD[5]}")
        keyframe_list = transnetv2.get_keyframe_transnet(opt.input_file, frame_count)

    log.debug_log(f"Keyframe Raw list {keyframe_list}")

    if len(keyframe_list) == 0:
        log.error_log("Keyframe list empty there are problem getting keyframe list")

    is_skip = opt.scd_method in predefined.SKIP_PROCESS_KEYFRAME or opt.ignore_scene_len
    keyframe_list1: list[int] = []

    if not is_skip:
        keyframe_list1 = keyframes.process_keyframe(keyframe_list, frame_count)
    else:
        # If skipping, just use the raw keyframe list as is
        # doing this to make sure list is int
        # because we skip process_keyframe
        keyframe_list1 = sorted([int(i) for i in keyframe_list])
        keyframes.warn_vid_frame(frame_count, keyframe_list1)

    log.debug_log("")  # empty line to split between raw keyframe and process keyframe
    log.debug_log(f"Keyframe Process list {keyframe_list1}")

    log.info_log(f"Keyframes Config {opt.enc_format}")
    enc_data = ""
    if opt.enc_format == predefined.ALL_CFG_OPT[0]:  # x264
        enc_data = cfg.get_scene_x264(keyframe_list1)
    elif opt.enc_format == predefined.ALL_CFG_OPT[1]:  # x265
        enc_data = cfg.get_scene_x265(keyframe_list)
    elif opt.enc_format == predefined.ALL_CFG_OPT[2]:  # svt-av1
        enc_data = cfg.get_scene_svtapp(keyframe_list1)
    elif opt.enc_format == predefined.ALL_CFG_OPT[3]:  # av1an
        enc_data = cfg.get_scene_av1an(keyframe_list1)
    elif opt.enc_format == predefined.ALL_CFG_OPT[4]:  # ffmpeg
        enc_data = cfg.get_scene_ffmpeg(keyframe_list1)
    elif opt.enc_format == predefined.ALL_CFG_OPT[5]:  # xav
        enc_data = cfg.get_scene_xav(keyframe_list1)

    if opt.output_file is not None:
        log.debug_log(f"Create folder at {opt.output_file.parent}")
        opt.output_file.parent.mkdir(parents=True, exist_ok=True)
        log.debug_log(f"Write file to {opt.output_file}")
        with open(opt.output_file, mode="w", encoding="utf-8") as f:
            f.write(enc_data)

    if opt.is_print:
        print(enc_data)
    else:
        print(get_print_final())
