import argparse
from av1_scd import predefined
from pathlib import Path

parser = argparse.ArgumentParser(description=f"py-video-encode {predefined.VERSION}")
parser.add_argument("-i", "--input", type=Path, required=True, help="Path to input file")
parser.add_argument("-o", "--output", type=Path, help="Path to output file")
parser.add_argument(
    "--min-scene-len",
    type=int,
    default=-2,
    help="min lenght for scene detection | Default is 1 sec of video",
)
parser.add_argument(
    "--max-scene-len",
    type=int,
    default=-2,
    help="max lenght for scene detection | Default is 10 sec of video",
)
parser.add_argument(
    "--scd-method",
    type=str,
    choices=predefined.ALL_SCD_METHOD,
    help="scene detection method | Default is pyscene",
    default=predefined.ALL_SCD_METHOD[0],
)
parser.add_argument(
    "--track",
    type=int,
    default=1,
    help="Track number for video (Index start at 1) | Default is 1",
)
parser.add_argument(
    "-f",
    "--format",
    required=True,
    type=str,
    choices=predefined.ALL_CFG_OPT,
    help="format of keyframe to feed program",
)
parser.add_argument(
    "--print",
    action="store_true",
    default=False,
    help="print data to stdout. this will disable the last helper massage",
)
parser.add_argument(
    "--log-level",
    type=str,
    choices=predefined.ALL_LOG_LEVEL,
    default=predefined.ALL_LOG_LEVEL[1],
    help="log level output to console | Default is info",
)
parser.add_argument(
    "--threshold",
    type=float,
    default=-2,
    help="treshold for scene change. Only affect pyscene and ffmpeg scd based method",
)
parser.add_argument(
    "--ignore-scene-len",
    action="store_true",
    default=False,
    help="skip keyframe processing that make scene len lenght "
    "exactly follow the value if method does not expose way to "
    "set min or max value of scene. This is not the same as 1 min "
    "and 9999 max scene len",
)
parser.add_argument(
    "--version",
    action="version",
    version=f"%(prog)s {predefined.VERSION}",
    help="print version",
)

parser1 = parser.add_argument_group(
    "pyscene", description="Extra option for pyscene scene detection method"
)
parser1.add_argument(
    "--pysc-decode",
    choices=predefined.ALL_PYSC_DECODE,
    type=str,
    default=predefined.ALL_PYSC_DECODE[0],
    help="Decode method for pyscene detect | Default is opencv",
)
parser1.add_argument(
    "--pysc-method",
    choices=predefined.ALL_PYSC_METHOD,
    type=str,
    default=predefined.ALL_PYSC_METHOD[0],
    help="Scene detect method for pyscene detect | Default is adaptive",
)


def PYSC_DOWNSCALE(value):
    if value == "auto":
        return value
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be 'auto' or an integer")


parser1.add_argument(
    "--pysc-downscale",
    type=PYSC_DOWNSCALE,
    default="auto",
    help="Downscale factor for pyscene detect method, "
    "can be either auto or number(int). "
    "To disable set this to 1 | Default is auto ",
)

parser2 = parser.add_argument_group(
    "vapoursynth",
    description="Extra option for vapousynth to perform vs-xvid scene detection method",
)
parser2.add_argument(
    "--vs-source",
    type=str,
    choices=predefined.ALL_VS_SOURCE,
    default=predefined.ALL_VS_SOURCE[1],
    help="Source method for vapoursynth | Default is ffms2",
)
parser2.add_argument(
    "--vsxvid-height",
    type=int,
    help="Height for vsxvid processing | Default is video height",
)
parser3 = parser.add_argument_group("transnet", "Extra option for transnetv2 model")
parser3.add_argument(
    "--transnet-model", type=str, help="Path to onnx transet model", default=None
)
parser4 = parser.add_argument_group("av-scenechnage", "Extra option for av-scenechange")
parser4.add_argument(
    "--ffmpeg-filter",
    type=str,
    help="Extra option to go in to -filter:v in ffmpeg for piping. "
    "Useful for downscaling video if select the binary mode",
)

parser4.add_argument(
    "--avsc-analyze-speed",
    type=str,
    choices=predefined.ALL_AVSC_SPEED,
    default=predefined.ALL_AVSC_SPEED[0],
    help="Set av-scenechange analysis speed | Default is standard",
)
parser4.add_argument(
    "--avsc-detect-flashes",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="Enable or disable av-scenechange flash detection",
)


def AVSC_LOOKAHEAD(value):
    try:
        value1 = int(value)
        if value1 < 1:
            raise argparse.ArgumentTypeError("must be integer more than 0")
        return value1
    except ValueError:
        raise argparse.ArgumentTypeError("must be integer")


parser4.add_argument(
    "--avsc-lookahead",
    type=AVSC_LOOKAHEAD,
    default=5,
    help="Set custom av-scenechange lookahead distance the value "
    "must be an integer more than 0 | Default is 5",
)

parser4.add_argument(
    "--avsc-score-mode",
    type=str,
    choices=predefined.ALL_AVSC_SCORE_MODE,
    default=predefined.ALL_AVSC_SCORE_MODE[0],
    help="Scenechange calculation mode if select xav score will "
    "using weight score logic (xav score mode is only support "
    "if you select the python binding mode) | Default is none",
)

parser4.add_argument(
    "--avsc-mode",
    choices=predefined.ALL_AVSC_MODE,
    default=predefined.ALL_AVSC_MODE[0],
    help="Select whether to use native python binding or binary | Default is binary",
)

parser4.add_argument(
    "--avsc-width",
    type=int,
    help="Video width use to detect scenechange. Useful for downscaling video",
)
parser4.add_argument(
    "--avsc-height",
    type=int,
    help="Video height use to detect scenechange. Useful for downscaling video",
)

args = parser.parse_args()

input_file: Path = args.input
output_file: Path | None = args.output if args.output else None
scd_method: str = args.scd_method
min_scene_len: int = args.min_scene_len
max_scene_len: int = args.max_scene_len
pysc_decode: str = args.pysc_decode
pysc_method: str = args.pysc_method
pysc_down_factor: str | int = args.pysc_downscale
vs_source: str = args.vs_source
user_track: int = args.track - 1
enc_format: str = args.format
is_print: bool = args.print
log_level: str = args.log_level
threshold: float = args.threshold
transnet_model_path: str | None = args.transnet_model
vsxvid_height: int = args.vsxvid_height
ffmpeg_filter: str = args.ffmpeg_filter
ignore_scene_len: bool = args.ignore_scene_len
avsc_analyze_speed: str = args.avsc_analyze_speed
avsc_detect_flashes: bool = args.avsc_detect_flashes
avsc_lookahead: int = args.avsc_lookahead
avsc_score_mode: str = args.avsc_score_mode
avsc_mode: str = args.avsc_mode
avsc_width: int | None = args.avsc_width
avsc_height: int | None = args.avsc_height
