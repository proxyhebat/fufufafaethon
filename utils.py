import os
import subprocess

import whisper
import yt_dlp


def progress(d):
    if d["status"] == "downloading":
        print(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']} ETA: {d['_eta_str']}")
    elif d["status"] == "finished":
        print(f"Done downloading, now post-processing... {d['filename']}")


def download_video(video_url, output_dir=None):
    if output_dir is None:
        output_dir = os.getcwd()

        output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

        try:
            with yt_dlp.YoutubeDL(
                {  # options
                    "format": "best",
                    "outtmpl": output_template,
                    "noplaylist": True,
                    "quiet": True,
                    "progress_hooks": [progress],
                }
            ) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                if "filepath" in info_dict:
                    return info_dict["filepath"]
                else:
                    file_name = ydl.prepare_filename(info_dict)
                    return os.path.join(output_dir, file_name)
        except:
            print("Error downloading video")
            return None


def extract_audio(video_path):
    print(f"extracting {video_path}")
    output_path = f"{video_path}.wav"
    cmd = f"ffmpeg -i '{video_path}' -ab 160k -ac 2 -ar 44100 -vn {output_path} -y"
    print(f"running command `{cmd}`")
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            video_path,
            "-ab",
            "160k",
            "-ac",
            "2",
            "-ar",
            "44100",
            "-vn",
            output_path,
            "-y",
        ],
        check=True,
    )
    return output_path


def transcribe(audio_path, model):
    print(f"Loading Whisper model: {model}")
    model = whisper.load_model(model)

    print(f"Transcribing {audio_path} using whisper {model}")
    result = model.transcribe(audio_path)

    # Extract segments
    segments = []
    for segment in result["segments"]:
        segments.append(
            {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"],
                "words": segment.get("words", []),
            }
        )

    return result["text"], segments
