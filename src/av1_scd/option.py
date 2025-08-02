import argparse
import shutil
from av1_scd import predefined
import importlib.util as imu


parser = argparse.ArgumentParser(description=f"py-video-encode {predefined.VERSION}")
parser.add_argument("-i", "--input", type=str, required=True, help="Path to input file.")
parser.add_argument("-o", "--output", type=str, help="Path to output file.")
parser.add_argument(
    "--min-scene-len", type=int, default=-2, help="min lenght for scene detection"
)
parser.add_argument(
    "--max-scene-len", type=int, default=-2, help="max lenght for scene detection"
)
ALL_SCD_METHOD = ["pyscene", "vsxvid", "av-scenechange"]
parser.add_argument(
    "--scd-method",
    type=str,
    choices=ALL_SCD_METHOD,
    help="scene detection method",
    default=ALL_SCD_METHOD[0],
)
parser.add_argument(
    "--track",
    type=int,
    default=1,
    help="Track number for video (Index start at 1). Default is 1",
)
ALL_CFG_OPT = ["x264", "x265", "svt-av1", "av1an", "av1an-git", "ffmpeg"]
parser.add_argument(
    "-f",
    "--format",
    required=True,
    type=str,
    choices=ALL_CFG_OPT,
    help="format of keyframe to feed program.",
)
parser.add_argument(
    "--print",
    action="store_true",
    default=False,
    help="print data to stdout. this will disable the last helper massage.",
)
LOG_LEVEL = ["debug", "info", "warning", "error"]
parser.add_argument(
    "--log-level",
    type=str,
    choices=LOG_LEVEL,
    default=LOG_LEVEL[1],
    help="log level output to console. Default is info.",
)
# parser.add_argument('--hw-decode', action='store_true', default=False,
# help='use hw acceleration to decode video')

parser1 = parser.add_argument_group(
    "pyscene", description="extra option for pyscene scene detection method"
)
_VALID_METHOD1 = ["opencv", "pyav", "moviepy"]
parser1.add_argument(
    "--pysc-decode",
    choices=_VALID_METHOD1,
    type=str,
    default=_VALID_METHOD1[0],
    help="Decode method for pyscene detect. Default is opencv.",
)
_VALID_METHOD2 = ["adaptive", "content", "threshold", "hash", "histogram"]
parser1.add_argument(
    "--pysc-method",
    choices=_VALID_METHOD2,
    type=str,
    default=_VALID_METHOD2[0],
    help="Scene detect method for pyscene detect. Default is adaptive.",
)
_VALID_METHOD3 = ["auto", int]
parser1.add_argument(
    "--pysc-downscale",
    choices=_VALID_METHOD3,
    type=str or int,
    default=_VALID_METHOD3[0],
    help="Downscale factor for pyscene detect method, "
    "can be either auto or number(int). "
    "To disable set this to 1. Default is auto.",
)

parser2 = parser.add_argument_group(
    "vapoursynth",
    description="extra option for vapousynth to perform vs-xvid scene detection method",
)
_VALID_METHOD4 = ["bestsource", "ffms2", "lsmash"]
parser2.add_argument(
    "--vs-source",
    type=str,
    choices=_VALID_METHOD4,
    default=_VALID_METHOD4[1],
    help="Source method for vapoursynth. Default is ffms2.",
)


args = parser.parse_args()

input_file: str = args.input
output_file: str = args.output
scd_method: str = args.scd_method
min_scene_len: int = args.min_scene_len
max_scene_len: int = args.max_scene_len
pysc_decode: str = args.pysc_decode
pysc_method: str = args.pysc_method
pysc_down_factor: int = args.pysc_downscale
vs_source: str = args.vs_source
user_track: int = args.track - 1
enc_format: str = args.format
is_print: bool = args.print
log_level: str = args.log_level


def get_lib() -> dict[str, bool]:
    available_lib = {
        "vapoursynth": False,
        "pyscene": False,
        "av_scenechange": False,
        "ffmpeg": False,
        "mediainfo": False,
        "vstools": False,
        "opencv": False,
        "colorama": False,
        "termcolor": False,
        "tqdm": False,
    }

    available_lib["vapoursynth"] = True if imu.find_spec("vapoursynth") else False

    available_lib["vstools"] = True if imu.find_spec("vstools") else False

    available_lib["mediainfo"] = True if imu.find_spec("mediainfo") else False

    available_lib["opencv"] = True if imu.find_spec("cv2") else False

    available_lib["colorama"] = True if imu.find_spec("colorama") else False

    available_lib["termcolor"] = True if imu.find_spec("termcolor") else False

    available_lib["tqdm"] = True if imu.find_spec("tdqm") else False

    available_lib["pyscene"] = True if imu.find_spec("scenedetect") else False

    av_scene_path = shutil.which("av-scenechange")
    if av_scene_path is not None:
        available_lib["av_scenechange"] = True

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is not None:
        available_lib["ffmpeg"] = True

    return available_lib


def validate_lib() -> None:
    lib_dict = get_lib()

    if not lib_dict["colorama"]:
        print("colorama is unavailable. install it with\npip install colorama")
    if not lib_dict["termcolor"]:
        print("termcolor is unavailable. install it with\npip install termcolor")

    from . import log

    if lib_dict["mediainfo"]:
        log.error_log(
            "pymediainfo is unavailable. install it with\n pip install pymediainfo"
        )
    if scd_method == ALL_SCD_METHOD[0] and not lib_dict["pyscene"]:
        log.error_log(
            f"{ALL_SCD_METHOD[0]} method is unavailable. install it with\n"
            "pip install scenedetect"
        )
    if scd_method == ALL_SCD_METHOD[1] and (
        not lib_dict["vapoursynth"] or not lib_dict["vstools"]
    ):
        if not lib_dict["vapoursynth"]:
            log.error_log(
                f"{ALL_SCD_METHOD[1]} method is unavailable. install vapoursynth"
            )
        else:
            log.error_log(
                f"{ALL_SCD_METHOD[2]} method is unavailable. install it with\n"
                "pip install vstools"
            )
    if (
        scd_method == ALL_SCD_METHOD[2]
        and (not lib_dict["av_scenechange"] or not lib_dict["ffmpeg"])
        and not lib_dict["tqdm"]
    ):
        if not lib_dict["ffmpeg"]:
            log.error_log("ffmepg is unavailable. install ffmpeg to the path")
        elif not lib_dict["av_scenechange"]:
            log.error_log(
                f"{ALL_SCD_METHOD[2]} method is unavailable. "
                "install av-scenechange binary to path"
            )
        elif not lib_dict["tqdm"]:
            log.error_log("tqdm is unavilable. install it with\npip install tqdm")

    log.debug_log(f"All Library Check {lib_dict}")
