import shutil
import subprocess
from av1_scd import option, util
import json
import tqdm
import threading
from pathlib import Path


min_kf_dist = option.min_scene_len
max_kf_dist = option.max_scene_len


def get_keyframe_avscenechange(input_path: Path, pix_fmt: str, frame_count: int) -> list:
    params1 = [shutil.which('ffmpeg'), '-progress', 'pipe:2', '-loglevel', 'error' ,
               '-hide_banner', '-i', input_path, '-map', '0:v:0', '-pix_fmt', pix_fmt,
               '-f', 'yuv4mpegpipe', '-strict', '-1', '-']  # fmt: skip

    params2 = [shutil.which('av-scenechange'), '-',
              '--speed', '0', '--min-scenecut', min_kf_dist,
              '--max-scenecut', max_kf_dist]  # fmt: skip

    params1 = [str(i) for i in params1]
    params2 = [str(i) for i in params2]

    with tqdm.tqdm(total=frame_count, desc="Processing frames") as pbar:
        p1 = subprocess.Popen(params1, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True)  # fmt: skip
        p2 = subprocess.Popen(params2, stdin=p1.stdout, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, text=True)  # fmt: skip

        if p1.stdout:
            p1.stdout.close()  # Let av-scenechange fully own the pipe

        def read_stderr():
            if p1.stderr:
                for line in p1.stderr:
                    util.track_ffmepg_progress(line, pbar)

        t = threading.Thread(target=read_stderr)
        t.start()

        stdout_data, _ = p2.communicate()
        p1.wait()
        t.join()

        pbar.n = frame_count
        pbar.refresh()
        pbar.close()

    scene_list = _process_scene_data(stdout_data)
    return scene_list


def _process_scene_data(content: str) -> list:
    scene_list = []

    json_data = json.loads(content)

    sc_list = json_data["scene_changes"]
    for fr in sc_list:
        scene_list.append(fr)

    # insert last frame of the video
    scene_list.append(json_data["frame_count"])

    return [fr for fr in scene_list]
