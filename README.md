# av1-scd

Tool to quickly detect scene change and generate config file for encoder to force keyframe for Encoding video.

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

## Support scene detection method

- [Pyscenedetect](https://github.com/Breakthrough/PySceneDetect)
- [WWXD](https://github.com/dubhater/vapoursynth-wwxd) and [Scxvid](https://github.com/dubhater/vapoursynth-scxvid) (vapoursynth)
- [av-scenechange](https://github.com/rust-av/av-scenechange)

## Dependencies

This is not require dependencies for a full list for python packages checkout requirements.txt\
if any dependencies is missing it will error out anyway.

- [Pymediainfo](https://github.com/sbraz/pymediainfo)
- [Pyscenedetect](https://github.com/Breakthrough/PySceneDetect)
- [vapoursynth](https://github.com/vapoursynth/vapoursynth)
- [ffmpeg](https://www.ffmpeg.org/)
- [av-scenechange](https://github.com/rust-av/av-scenechange)

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

## Installation

wheel build file available in release

## Build from Source

1. Build wheel

   ```bash
   git clone https://github.com/Khaoklong51/av1-scd.git
   cd av1-scd
   python -m build --wheel # or 'uv build' if you have uv.
   pipx install dist/*.whl
    ```

2. Pyinstaller (experimental)

   ```bash
   pyinstaller av1-scd.spec --clean
   ```

## Usage

`av1-scd -i input.mp4 -o x265.cfg -f x265`

## Parameter

```text
usage: av1-scd [-h] -i INPUT -o OUTPUT [--min-scene-len MIN_SCENE_LEN] [--max-scene-len MAX_SCENE_LEN] [--scd-method {pyscene,vsxvid,av-scenechange}] [--track TRACK]
               -f {x264,x265,svt-av1,av1an,av1an-git,ffmpeg} [--print] [--log-level {debug,info,warning,error}] [--pysc-decode {opencv,pyav,moviepy}]
               [--pysc-method {adaptive,content,threshold,hash,histogram}] [--pysc-downscale {auto,<class 'int'>}] [--vs-source {bestsource,ffms2,lsmash}]

py-video-encode v1.0.0

options:
  -h, --help            show this help message and exit
  -i, --input INPUT     Path to input file.
  -o, --output OUTPUT   Path to output file.
  --min-scene-len MIN_SCENE_LEN
                        min lenght for scene detection
  --max-scene-len MAX_SCENE_LEN
                        max lenght for scene detection
  --scd-method {pyscene,vsxvid,av-scenechange}
                        scene detection method
  --track TRACK         Track number for video (Index start at 1). Default is 1
  -f, --format {x264,x265,svt-av1,av1an,av1an-git,ffmpeg}
                        format of keyframe to feed program.
  --print               print data to stdout. this will disable the last helper massage.
  --log-level {debug,info,warning,error}
                        log level output to console. Default is info.

pyscene:
  extra option for pyscene scene detection method

  --pysc-decode {opencv,pyav,moviepy}
                        Decode method for pyscene detect. Default is opencv.
  --pysc-method {adaptive,content,threshold,hash,histogram}
                        Scene detect method for pyscene detect. Default is adaptive.
  --pysc-downscale {auto,<class 'int'>}
                        Downscale factor for pyscene detect method, can be either auto or number(int). To disable set this to 1. Default is auto.

vapoursynth:
  extra option for vapousynth to perform vs-xvid scene detection method

  --vs-source {bestsource,ffms2,lsmash}
                        Source method for vapoursynth. Default is ffms2.
```
