import argparse
from av1_scd import predefined


parser = argparse.ArgumentParser(description=f"py-video-encode {predefined.VERSION}")
parser.add_argument("-i", "--input", type=str, required=True, help="Path to input file.")
parser.add_argument("-o", "--output", type=str, help="Path to output file.")
parser.add_argument(
    "--min-scene-len",
    type=int,
    default=-2,
    help="min lenght for scene detection. Default is 1 sec of video",
)
parser.add_argument(
    "--max-scene-len",
    type=int,
    default=-2,
    help="max lenght for scene detection. Default is 10 sec of viddeo",
)
ALL_SCD_METHOD = [
    "pyscene",
    "vsxvid",
    "av-scenechange",
    "ffmpeg-scene",
    "ffmpeg-scdet",
    "transnetv2",
]
parser.add_argument(
    "--scd-method",
    type=str,
    choices=ALL_SCD_METHOD,
    help="scene detection method. Default is pyscene",
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
parser.add_argument(
    "--treshold", type=float, default=-2, help="treshold for scene change"
)
# parser.add_argument("--hw-decode", action="store_true", default=False,
# help="use hw acceleration to decode video")

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
parser2.add_argument(
    "--vsxvid-height",
    type=int,
    default=None,
    help="Height for vsxvid processing. Default is video height.",
)

parser3 = parser.add_argument_group("transnet", "Extra option for transnetv2 model")
parser3.add_argument(
    "--transnet-model", type=str, default=None, help="Path to onnx transet model"
)


args = parser.parse_args()

input_file: str = args.input
output_file: str = args.output
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
treshold: float = args.treshold
transnet_model_path: str | None = args.transnet_model
vsxvid_height: int | None = args.vsxvid_height
