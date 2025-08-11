VERSION = "v1.0.0"

FF_PIXFMT = {
    # list of supported yuv4mpeg format
    "YUV411P8": "yuv411p",
    "YUV420P8": "yuv420p",
    "YUV420P9": "yuv420p9le",
    "YUV420P10": "yuv420p10le",
    "YUV420P12": "yuv420p12le",
    "YUV420P14": "yuv420p14le",
    "YUV420P16": "yuv420p16le",
    "YUV422P8": "yuv422p",
    "YUV422P9": "yuv422p9le",
    "YUV422P10": "yuv422p10le",
    "YUV422P12": "yuv422p12le",
    "YUV422P14": "yuv422p14le",
    "YUV422P16": "yuv422p16le",
    "YUV444P8": "yuv444p",
    "YUV444P10": "yuv444p10le",
    "YUV444P12": "yuv444p12le",
    "YUV444P14": "yuv444p14le",
    "YUV444P16": "yuv444p16le",
    "GRAYP8": "gray",
    "GRAYP16": "gray16le",
    "YUVJ420P8": "yuv420p",
    "YUVJ422P8": "yuv422p",
    "YUVJ444P8": "yuv444p",
}

THRESHOLD = {
    "pysc-adaptive": 3.0,
    "pysc-content": 27.0,
    "pysc-hash": 0.395,
    "pysc-histogram": 0.05,
    "pysc-threshold": 12.0,
    "ffmpeg-scene": 0.4,
    "ffmpeg-scdet": 10.0,
    "transnetv2": 0.5,
}

GPU_PROVIDER = {
    "MIGraphXExecutionProvider",
    "CUDAExecutionProvider",
    "DirectMLExecutionProvider",
    "ROCMExecutionProvider",
}

# reserve for future use incase other method add
SKIP_PROCESS_KEYFRAME = {
    "transnetv2",
}
