import pymediainfo as pym
from av1_scd import log, predefined, option
import typing as typ

vid_data = dict[str, typ.Any]
FF_PIXEL = predefined.FF_PIXFMT


def get_pymediainfo_data(input_path: str) -> vid_data:
    user_track = option.user_track
    media_info = pym.MediaInfo.parse(input_path, parse_speed=1)
    track_list: list[pym.Track] = media_info.video_tracks
    num_tracks = len(track_list)
    if user_track >= num_tracks or user_track < 0:
        log.error_log(
            f"Invalid Track: {user_track + 1}, "
            "only {num_tracks} video tracks available."
        )

    log.debug_log(f"Track data {str(track_list[user_track].to_data())}")
    # already return dict data of selected track
    return track_list[user_track].to_data()


def get_ffmpeg_pixfmt(track_data: vid_data) -> str:
    color_space: str = track_data["color_space"]
    chroma_sub: str = track_data["chroma_subsampling"].replace(":", "")
    bit_depth: int = track_data["bit_depth"]

    pix_format = f"{color_space}{chroma_sub}P{bit_depth}"

    ffmpeg_pix_format = FF_PIXEL[pix_format]
    if ffmpeg_pix_format is None:
        log.warning_log("Cannot get pixel format. fallback to yuv420p")
        ffmpeg_pix_format = "yuv420p"
    log.debug_log(f"FFmpeg pixel format {str(FF_PIXEL[pix_format])}")
    return ffmpeg_pix_format


def get_vid_height(track_data: vid_data) -> int:
    log.debug_log(f"Video height {str(track_data['height'])}")
    return int(track_data["height"])


def get_frame_count(track_data: vid_data) -> int:
    log.debug_log(f"Framecount {str(track_data['frame_count'])}")
    return int(track_data["frame_count"])


def get_scene_len(track_data: vid_data) -> tuple[int, int]:
    log.debug_log(f"Framerate {str(track_data['frame_rate'])}")
    frame_rate = float(track_data["frame_rate"])
    min_len = round(frame_rate)
    max_len = round(frame_rate * 5)
    return min_len, max_len
