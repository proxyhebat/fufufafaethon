import argparse
import subprocess

import validators
from moviepy import CompositeVideoClip, TextClip, VideoFileClip

from utils import LLMClipFinder, download_video, transcribe


def get_text_clips(transcription_result):
    text_clip_array = []
    segments = transcription_result["segments"]
    for segment in segments:
        for word in segment["words"]:
            text_clip_array.append(
                TextClip(
                    text=word["text"], font_size=90, stroke_color="black", stroke_width=8, color="white", font="Arial"
                )
                .with_start(word["start"])
                .with_end(word["end"])
                .with_position("center")
            )

    return text_clip_array


def main():
    parser = argparse.ArgumentParser(description="AI powered video clipper")
    parser.add_argument("video_url", help="YouTube video URL or path to a video")
    parser.add_argument("--api-key", help='your google genai api key e.g. --api-key="AIza..."')
    parser.add_argument("--prompt", help='your prompt e.g. --prompt="most interesting moments"')
    parser.add_argument("--categories", help='comma seperated e.g. --categories="Fashion, Bokep, Finansial 😭"')
    parser.add_argument("--model", help="whisper model")

    args = parser.parse_args()

    if validators.url(args.video_url):
        args.video_url = download_video(args.video_url)

    transcription_result = transcribe(args.video_url, model=args.model or "base")
    text_clips = get_text_clips(transcription_result)

    cf = LLMClipFinder(args.api_key)
    result = cf.find_interesting_moments(args.prompt, transcription_result["segments"])

    clips = []
    for clip in result["clips"]:
        start = clip["start"]
        end = clip["end"]
        output_name = f"{clip['caption']}.mp4"
        subprocess.run(
            ["ffmpeg", "-i", f"{args.video_url}", "-ss", start, "-to", end, "-c", "copy", output_name],
            check=True,
        )
        clips.append(output_name)

    for clip in clips:
        video = VideoFileClip(clip)
        final_video = CompositeVideoClip([video] + text_clips)
        final_video.write_videofile(f"result-{clip}")


if __name__ == "__main__":
    main()
