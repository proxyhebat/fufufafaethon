import argparse

from utils import LLMClipFinder, download_video, extract_audio, transcribe


def main():
    parser = argparse.ArgumentParser(description="AI powered video clipper")
    parser.add_argument("video_url", help="YouTube video URL")
    parser.add_argument("--api-key", help='your google genai api key e.g. --api-key="AIza..."')
    parser.add_argument("--prompt", help='your prompt e.g. --prompt="most interesting moments"')
    parser.add_argument("--categories", help='comma seperated e.g. --categories="Fashion, Bokep, Finansial 😭"')

    args = parser.parse_args()

    video_path = download_video(args.video_url)
    if video_path is None:
        print("[fufufafaethon.py] No video path supplied. Exiting program.")
        return 1

    audio_path = extract_audio(video_path)
    if audio_path is None:
        print("[fufufafaethon.py] No audio path supplied. Exiting program.")
        return 1

    segments = transcribe(audio_path, model="turbo")
    print("segment", segments)
    cf = LLMClipFinder(args.api_key)
    result = cf.find_interesting_moments(args.prompt, segments)
    print("genai result", result)


if __name__ == "__main__":
    main()
