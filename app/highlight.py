def pick_highlights(scenes, transcript):
    # basic logic: pick first few non-empty scenes
    highlights = [scene for scene in scenes if scene["end"] - scene["start"] > 0.5][:3]
    return highlights