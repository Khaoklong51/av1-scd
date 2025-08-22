import argparse
from av1_scd import predefined
from pathlib import Path


ALL_VAPOURSYNTH_DECODE = predefined.ALL_VS_SOURCE
ALL_SCD_METHOD = predefined.ALL_SCD_METHOD
ALL_CFG_OPT = predefined.ALL_CFG_OPT
ALL_LOG_LEVEL = predefined.ALL_LOG_LEVEL
ALL_PYSCENE_DECODE = predefined.ALL_PYSC_DECODE
ALL_PYSCENE_METHOD = predefined.ALL_PYSC_METHOD
PYSC_DOWNSCALE = predefined.PYSC_DOWNSCALE


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
parser.add_argument(
    "--log-level",
    type=str,
    choices=ALL_LOG_LEVEL,
    default=ALL_LOG_LEVEL[1],
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
parser1.add_argument(
    "--pysc-decode",
    choices=ALL_PYSCENE_DECODE,
    type=str,
    default=ALL_PYSCENE_DECODE[0],
    help="Decode method for pyscene detect. Default is opencv.",
)
parser1.add_argument(
    "--pysc-method",
    choices=ALL_PYSCENE_METHOD,
    type=str,
    default=ALL_PYSCENE_METHOD[0],
    help="Scene detect method for pyscene detect. Default is adaptive.",
)
parser1.add_argument(
    "--pysc-downscale",
    choices=PYSC_DOWNSCALE,
    type=str or int,
    default=PYSC_DOWNSCALE[0],
    help="Downscale factor for pyscene detect method, "
    "can be either auto or number(int). "
    "To disable set this to 1. Default is auto.",
)

parser2 = parser.add_argument_group(
    "vapoursynth",
    description="extra option for vapousynth to perform vs-xvid scene detection method",
)
parser2.add_argument(
    "--vs-source",
    type=str,
    choices=ALL_VAPOURSYNTH_DECODE,
    default=ALL_VAPOURSYNTH_DECODE[1],
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
parser4 = parser.add_argument_group("av-scenechnage", "Extraoption for av-scenechange")
parser4.add_argument(
    "--ffmpeg-filter",
    type=str,
    default=None,
    help="Extra option to go in to -filter:v:0 in ffmpeg for piping. "
    "Useful for downscaling video",
)

args = parser.parse_args()

input_file: Path = Path(args.input)
output_file1: str | None = args.output
output_file = Path("")
if output_file1 is not None:
    output_file = Path(output_file1)
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
transnet_model_path1 = args.transnet_model
transnet_model_path = Path("")
if transnet_model_path1 is not None:
    transnet_model_path = Path(transnet_model_path1)
vsxvid_height: int | None = args.vsxvid_height
ffmpeg_filter: str | None = args.ffmpeg_filter
