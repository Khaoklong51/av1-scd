from . import option

def process_keyframe(keyframes: list[int], frame_count: int) -> list[int]:
    min_kf_dist = option.min_scene_len
    max_kf_dist = option.max_scene_len

    keyframes_a = sorted(int(fr) for fr in keyframes)

    if keyframes_a[0] != 0:
        keyframes_a.insert(0, 0)
    if keyframes_a[-1] != frame_count:
        keyframes_a.append(frame_count)

    keyframes_cut = [keyframes_a[0]]

    for i in range(1, len(keyframes_a)):
        prev = keyframes_a[i - 1]
        curr = keyframes_a[i]
        frame_diff = curr - prev

        # Insert intermediate keyframes if too long
        x = 1
        while frame_diff >= max_kf_dist and (curr - (prev + max_kf_dist * x)) >= min_kf_dist:
            split_point = prev + max_kf_dist * x
            keyframes_cut.append(split_point)
            x += 1

        # Add this keyframe if far enough from previous
        if (curr - keyframes_cut[-1]) >= min_kf_dist:
            keyframes_cut.append(curr)

    keyframes_cut = sorted(set(keyframes_cut))  # remove duplicates
    return keyframes_cut
