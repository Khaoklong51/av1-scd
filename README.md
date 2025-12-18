# av1-scd

Command line tool to quickly detect scene change and generate config file for encoder to force keyframe for Encoding video.

- [Installation](#installtion)
- [Encoder format](#support-encoder-format)
- [Scene detection method](#support-scene-detection-method)
- [Dependencies](#dependencies)
- [Checking Keyframe of video](#checking-keyframe-of-video)
- [Usage](#usage)
- [Parameter](#parameter)

## Support encoder format

- [x264](https://www.videolan.org/developers/x264.html)
- [x265](https://www.videolan.org/developers/x265.html)
- [SvtAv1EncApp](https://gitlab.com/AOMediaCodec/SVT-AV1)
- [ffmpeg](https://www.ffmpeg.org/)
- [av1an](https://github.com/rust-av/Av1an)
- [xav](https://github.com/emrakyz/xav)

## Support scene detection method

- [Pyscenedetect](https://github.com/Breakthrough/PySceneDetect)
- [WWXD](https://github.com/dubhater/vapoursynth-wwxd) and [Scxvid](https://github.com/dubhater/vapoursynth-scxvid) (vapoursynth)
- [av-scenechange](https://github.com/rust-av/av-scenechange)
- [ffmpeg](https://www.ffmpeg.org/) (using scene score and scdet filter)
- [TransNetV2](https://github.com/soCzech/TransNetV2.git) This project use onnxruntime and opencv-python not tensorflow in the original project

## Dependencies

**This is not require dependencies** for a full list of dependencies checkout pyproject.toml\
if any dependencies is missing it will error out anyway.

- [Pymediainfo](https://github.com/sbraz/pymediainfo)
- [Pyscenedetect](https://github.com/Breakthrough/PySceneDetect)
- [vapoursynth](https://github.com/vapoursynth/vapoursynth)
- [ffmpeg](https://www.ffmpeg.org/)
- [av-scenechange](https://github.com/rust-av/av-scenechange)
- [opencv-python](https://github.com/opencv/opencv-python)
- [numpy](https://github.com/numpy/numpy)
- [tqdm](https://github.com/tqdm/tqdm.git)
- [onnxruntime](https://github.com/microsoft/onnxruntime)
- [TransetV2](https://github.com/soCzech/TransNetV2.git) The tensorflow model is in "inference/transnetv2-weights/model" folder of the original project if you want to use with this program you need onnx model which you can download [it here](https://huggingface.co/elya5/transnetv2/tree/main)

## Checking Keyframe of video

1. Use [LosslessCut](https://github.com/mifi/lossless-cut) to check
2. FFprobe command : The command list keyframe of video

- Bash (linux)

```bash
input="input.mkv"

# Get frame rate as decimal
fps=$(ffprobe -v 0 -select_streams v:0 -show_entries stream=r_frame_rate \
      -of default=nokey=1:noprint_wrappers=1 "$input" | awk -F'/' '{printf "%.0f", $1 / ($2 ? $2 : 1)}')

# Extract keyframe PTS and convert to frame number
ffprobe -loglevel error -select_streams v:0 \
  -show_entries packet=pts_time,flags -of csv=print_section=0 "$input" |
awk -F',' -v fps="$fps" '/K/ {printf "%.0f\n", $1 * fps}'
```

The report keyframe may differ slightly (usually 1,2 or 3 frames) depend on program (This is normal)

## Installtion

1. From [Pypi](https://pypi.org/project/av1-scd/)

   ```bash
   pipx install av1-scd # install with minimal dependencies
   pipx install av1-scd[vsxvid,transnet] # install with optional vsxvid and transnet dependencies. All option are [vsxvid, transnet, pyscene]
   ```

2. Build wheel

   ```bash
   git clone https://github.com/Khaoklong51/av1-scd.git
   cd av1-scd
   python -m build --wheel # or 'uv build' if you have uv.
   pipx install dist/*.whl # install with minimal dependencies
   pipx install dist/*.whl[vsxvid,transnet] # install with optional vsxvid and transnet dependencies. All option are [vsxvid, transnet, pyscene]
   ```

3. Wheel files

   Wheel file can be download at [release](https://github.com/Khaoklong51/av1-scd/releases) section\
   \
   then install with pipx or your prefered package manager

   ```bash
   pipx install av1-scd.whl # install with minimal dependencies
   pipx install av1-scd.whl[vsxvid,transnet] # install with optional vsxvid and transnet dependencies. All option are [vsxvid, transnet, pyscene]
   ```

## Usage

`av1-scd -i input.mp4 -o x265.cfg -f x265`

## Parameter

```text
usage: av1-scd [-h] -i INPUT [-o OUTPUT] [--min-scene-len MIN_SCENE_LEN] [--max-scene-len MAX_SCENE_LEN]
               [--scd-method {pyscene,vsxvid,av-scenechange,ffmpeg-scene,ffmpeg-scdet,transnetv2}] [--track TRACK] -f {x264,x265,svt-av1,av1an,av1an-git,ffmpeg,xav}
               [--print] [--log-level {debug,info,warning,error}] [--treshold TRESHOLD] [--ignore-scene-len] [--version] [--pysc-decode {opencv,pyav,moviepy}]
               [--pysc-method {adaptive,content,threshold,hash,histogram}] [--pysc-downscale PYSC_DOWNSCALE] [--vs-source {bestsource,ffms2,lsmash}]
               [--vsxvid-height VSXVID_HEIGHT] [--transnet-model TRANSNET_MODEL] [--ffmpeg-filter FFMPEG_FILTER]

py-video-encode v3.0.0

options:
  -h, --help            show this help message and exit
  -i, --input INPUT     Path to input file.
  -o, --output OUTPUT   Path to output file.
  --min-scene-len MIN_SCENE_LEN
                        min lenght for scene detection. Default is 1 sec of video
  --max-scene-len MAX_SCENE_LEN
                        max lenght for scene detection. Default is 5 sec of viddeo
  --scd-method {pyscene,vsxvid,av-scenechange,ffmpeg-scene,ffmpeg-scdet,transnetv2}
                        scene detection method. Default is pyscene
  --track TRACK         Track number for video (Index start at 1). Default is 1
  -f, --format {x264,x265,svt-av1,av1an,av1an-git,ffmpeg,xav}
                        format of keyframe to feed program.
  --print               print data to stdout. this will disable the last helper massage.
  --log-level {debug,info,warning,error}
                        log level output to console. Default is info.
  --treshold TRESHOLD   treshold for scene change
  --ignore-scene-len    skip keyframe processing that make scene len lenght exactly follow the value if method does not expose way to set min or max value of scene.
                        This is not the same as 1 min and 9999 max scene len
  --version             print version

pyscene:
  Extra option for pyscene scene detection method

  --pysc-decode {opencv,pyav,moviepy}
                        Decode method for pyscene detect. Default is opencv.
  --pysc-method {adaptive,content,threshold,hash,histogram}
                        Scene detect method for pyscene detect. Default is adaptive.
  --pysc-downscale PYSC_DOWNSCALE
                        Downscale factor for pyscene detect method, can be either auto or number(int). To disable set this to 1. Default is auto.

vapoursynth:
  Extra option for vapousynth to perform vs-xvid scene detection method

  --vs-source {bestsource,ffms2,lsmash}
                        Source method for vapoursynth. Default is ffms2.
  --vsxvid-height VSXVID_HEIGHT
                        Height for vsxvid processing. Default is video height.

transnet:
  Extra option for transnetv2 model

  --transnet-model TRANSNET_MODEL
                        Path to onnx transet model

av-scenechnage:
  Extra option for av-scenechange

  --ffmpeg-filter FFMPEG_FILTER
                        Extra option to go in to -filter:v in ffmpeg for piping. Useful for downscaling video
```
