import shutil
import subprocess
import re
import tqdm
import threading
from av1_scd import predefined, log, util
from pathlib import Path
from av1_scd import option as opt


def get_keyframe_ffmpeg_scene(input_file: Path) -> list:
    local_threshold = opt.threshold
    if local_threshold == -2:
        local_threshold = predefined.THRESHOLD["ffmpeg-scene"]
    log.info_log(f"Select treshold {local_threshold}")
    log.warning_log(
        f"{predefined.ALL_SCD_METHOD[3]} method does not support progress bar"
    )
    command1 = [shutil.which("ffmpeg"), "-hide_banner",
                "-i", input_file, "-filter:v",
                rf"select=gt(scene\,{local_threshold}),showinfo",
                "-an", "-f", "null", "-"] # fmt: skip

    command1 = [str(i) for i in command1]
    p1 = subprocess.run(command1, stderr=subprocess.PIPE, text=True)
    line = []

    for i in p1.stderr.splitlines():
        if "showinfo" in i:
            match = re.search(r"pts_time:([0-9.]+)", i)
            if match:
                line.append(match.group(1))

    log.debug_log(f"FFmpeg basic {line}")
    return line


def get_keyframe_ffmpeg_scdet(input_file: Path, frame_count: int) -> list:
    local_threshold = opt.threshold
    if local_threshold == -2:
        local_threshold = predefined.THRESHOLD["ffmpeg-scdet"]

    command1 = [shutil.which("ffmpeg"), "-hide_banner",
                "-progress", "pipe:1", "-i", input_file,
                "-filter:v",
                f"scdet=t={local_threshold}",
                "-an", "-f", "null", "-"] # fmt: skip

    command1 = [str(i) for i in command1]
    ffmpeg_data = []
    with tqdm.tqdm(total=frame_count, desc="Processing frames", unit="fps") as pbar:
        p1 = subprocess.Popen(
            command1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        def read_stdout():
            if p1.stdout:
                for line in p1.stdout:
                    util.track_ffmepg_progress(line, pbar)

        def read_stderr():
            if p1.stderr:
                for line in p1.stderr:
                    ffmpeg_data.append(line)

        t_out = threading.Thread(target=read_stdout)
        t_err = threading.Thread(target=read_stderr)

        t_out.start()
        t_err.start()

        p1.wait()
        t_out.join()
        t_err.join()

        pbar.n = frame_count
        pbar.refresh()
        pbar.close()

    line = []

    for i in ffmpeg_data:
        if "lavfi.scd.time" in i:
            match = re.search(r"lavfi\.scd\.time: ([0-9.]+)", i)
            if match:
                line.append(match.group(1))

    log.debug_log(f"FFmpeg scdet {line}")
    return line
