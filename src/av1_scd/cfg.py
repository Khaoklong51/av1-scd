import json
import typing as type


def get_scene_av1an_git(scence_list: list[int]) -> str:
    class Scenedict(type.TypedDict):
        start_frame: int
        end_frame: int
        zone_overrides: None

    class Scenesjson(type.TypedDict):
        frames: int
        scenes: list[Scenedict]
        split_scenes: list[Scenedict]

    scenes_json: Scenesjson = {
        "frames": scence_list[-1],  # last frame in list
        "scenes": [],
        "split_scenes": [],
    }

    # don't need last frame
    for i in range(len(scence_list) - 1):
        dict_data: Scenedict = {
            "start_frame": scence_list[i],
            "end_frame": scence_list[i + 1],
            "zone_overrides": None,
        }
        scenes_json["scenes"].append(dict_data)
        scenes_json["split_scenes"].append(dict_data)

    return json.dumps(scenes_json, indent=4, allow_nan=True)


def get_scene_av1an(scence_list: list[int]) -> str:
    class Scenedict(type.TypedDict):
        start_frame: int
        end_frame: int
        zone_overrides: None

    class Scenesjson(type.TypedDict):
        frames: int
        scenes: list[Scenedict]
        split_scenes: list[Scenedict]

    scenes_json: Scenesjson = {
        "frames": scence_list[-1],  # last frame in list
        "scenes": [],
        "split_scenes": [],
    }

    # don't need last frame
    for i in range(len(scence_list) - 1):
        dict_data: Scenedict = {
            "start_frame": scence_list[i],
            "end_frame": scence_list[i + 1],
            "zone_overrides": None,
        }
        scenes_json["scenes"].append(dict_data)
        scenes_json["split_scenes"].append(dict_data)

    return json.dumps(scenes_json, indent=4, allow_nan=True)


def get_scene_svtapp(scene_list: list[int]) -> str:
    # don't need last frame
    scene_list.pop(-1)
    keyframes_data = f"ForceKeyFrames : {'f,'.join([str(i) for i in scene_list])}f"

    return keyframes_data


def get_scene_x264(scene_list: list[int]) -> str:
    # don't need last frame
    scene_list.pop(-1)
    cfg_data: str = ""

    for fr in scene_list:
        cfg_data += f"{fr} K -1\n"

    return cfg_data


def get_scene_x265(scene_list: list[int]) -> str:
    # don't need last frame
    scene_list.pop(-1)
    cfg_data: str = ""

    for fr in scene_list:
        cfg_data += f"{fr} K\n"

    return cfg_data


def get_scene_ffmpeg(scene_list: list[int]) -> str:
    # don't need last frame
    scene_list.pop(-1)
    cfg_data = "expr:"
    for i in scene_list:
        cfg_data += f"eq(n,{i})+"

    return cfg_data.removesuffix("+")


def get_scene_xav(scene_list: list[int]):

    scene_list.pop(-1)
    cfg_data = ""
    for fr in scene_list:
        cfg_data += f"{fr}\n"

    return cfg_data
