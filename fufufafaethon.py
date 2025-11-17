import argparse
import logging
import re
import subprocess

import validators
from moviepy import CompositeVideoClip, TextClip, VideoFileClip

from utils import LLMClipFinder, download_video, transcribe

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def sanitize_filename(name):
    name = re.sub(r"[^\w\s-]", "", name)  # Remove special chars except word, space, dash
    name = re.sub(r"\s+", "_", name)  # Replace spaces with underscores
    if len(name) > 100:
        name = name[:100]
    return name


def parse_time(time_str):
    minutes, seconds = map(int, time_str.split(":"))
    return minutes * 60 + seconds


def get_text_clips(transcription_result, clip_start, clip_end):
    text_clip_array = []
    segments = transcription_result["segments"]
    for segment in segments:
        for word in segment["words"]:
            if word["start"] >= clip_start and word["end"] <= clip_end:
                text_clip_array.append(
                    TextClip(
                        text=word["text"],
                        font_size=90,
                        stroke_color="black",
                        stroke_width=8,
                        color="white",
                        font="Arial",
                    )
                    .with_start(word["start"] - clip_start)
                    .with_end(word["end"] - clip_start)
                    .with_position("center")
                )

    return text_clip_array


def main():
    logger.info("Starting fufufafaethon video processing")
    parser = argparse.ArgumentParser(description="AI powered video clipper")
    parser.add_argument("video_url", help="YouTube video URL or path to a video")
    parser.add_argument("--api-key", help='your google genai api key e.g. --api-key="AIza..."')
    parser.add_argument("--prompt", help='your prompt e.g. --prompt="most interesting moments"')
    parser.add_argument("--categories", help='comma seperated e.g. --categories="Fashion, Bokep, Finansial 😭"')
    parser.add_argument("--model", help="whisper model")

    args = parser.parse_args()
    logger.info(f"Processing video: {args.video_url}")
    logger.info(f"Using prompt: {args.prompt or 'most interesting moments'}")
    logger.info(f"Whisper model: {args.model or 'base'}")

    if validators.url(args.video_url):
        logger.info("URL detected, downloading video")
        args.video_url = download_video(args.video_url)
    else:
        logger.info("Local video file provided")

    logger.info("Starting transcription")
    transcription_result = transcribe(args.video_url, model=args.model or "base")

    logger.info("Initializing LLM clip finder")
    cf = LLMClipFinder(args.api_key)

    logger.info("Finding interesting moments using LLM")
    result = cf.find_interesting_moments(args.prompt or "most interesting moments", transcription_result["segments"])
    logger.info(f"Found {len(result['clips'])} interesting clips")

    clips = []
    logger.info("Processing and creating video clips")
    for i, clip in enumerate(result["clips"]):
        start = clip["start"]
        end = clip["end"]
        output_name = f"{sanitize_filename(clip['caption'])}.mp4"
        logger.info(f"Creating clip {i + 1}/{len(result['clips'])}: {output_name} ({start} to {end})")

        subprocess.run(
            ["ffmpeg", "-i", f"{args.video_url}", "-ss", start, "-to", end, "-c", "copy", output_name],
            check=True,
        )
        clips.append(output_name)
        logger.debug(f"Clip {output_name} created successfully")

    logger.info("Composing final videos with text overlays")
    for i, clip_info in enumerate(result["clips"]):
        clip_file = clips[i]
        start = clip_info["start"]
        end = clip_info["end"]
        clip_start_sec = parse_time(start)
        clip_end_sec = parse_time(end)
        text_clips = get_text_clips(transcription_result, clip_start_sec, clip_end_sec)
        logger.info(f"Processing final video {i + 1}/{len(clips)}: {clip_file} with {len(text_clips)} text clips")
        video = VideoFileClip(clip_file)
        final_video = CompositeVideoClip([video] + text_clips)
        output_filename = f"result-{clip_file}"
        logger.info(f"Writing final video: {output_filename}")
        final_video.write_videofile(output_filename, audio_codec="aac")
        logger.info(f"Final video {output_filename} completed")

    logger.info("All video processing completed successfully")


if __name__ == "__main__":
    main()
