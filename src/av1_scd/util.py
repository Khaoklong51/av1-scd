import typing as typ
import tqdm
import re


def frame_time_to_num(ln: list[typ.Any], frame_rate: float) -> list[int]:
    ppu = [float(i) for i in ln]
    ppu.sort()
    x: list[int] = []
    for i in ppu:
        e = i * frame_rate
        if e >= 0:
            x.append(round(e))

    return x


def track_ffmepg_progress(text: str, pbar: tqdm.tqdm):
    match = re.search(r"frame=(\d+)", text)
    if match:
        frame = int(match.group(1))
        pbar.n = frame
        pbar.refresh()
