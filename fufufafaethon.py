import argparse


def main():
    parser = argparse.ArgumentParser(description="AI powered video clipper")
    parser.add_argument("video_url", help="YouTube video URL")
    parser.add_argument("--api-key", help='your google genai api key e.g. --api-key="AIza..."')
    parser.add_argument("--prompt", help='your prompt e.g. --prompt="most interesting moments"')
    parser.add_argument("--categories", help='comma seperated e.g. --categories="Fashion, Bokep, Finansial 😭"')

    args = parser.parse_args()
    print("[fufufafaethon.py] supplied args: ", args)


if __name__ == "__main__":
    main()
