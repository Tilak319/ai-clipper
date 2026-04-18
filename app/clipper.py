import subprocess
import os

def create_clip(input_path, start, end, output_path):
    duration = max(0.0, float(end) - float(start))
    if duration <= 0:
        raise ValueError(f"Invalid clip duration: start={start}, end={end}")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-ss", str(start),
        "-t", str(duration),
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        "-y",
        output_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr.strip()}")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError(f"Clip file was not created or is empty: {output_path}")


def generate_clips(video_path, highlights):
    clips = []

    for i, h in enumerate(highlights):
        output = f"outputs/clip_{i}.mp4"
        create_clip(video_path, h["start"], h["end"], output)
        clips.append(output)

    return clips