import logging
import os
import subprocess

import google.generativeai as genai
import whisper_timestamped as whisper
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def progress(d):
    if d["status"] == "downloading":
        print(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']} ETA: {d['_eta_str']}")
    elif d["status"] == "finished":
        print(f"Done downloading, now post-processing... {d['filename']}")


def download_video(video_url, output_dir=None):
    logger.info(f"Starting video download from URL: {video_url}")
    if output_dir is None:
        output_dir = os.getcwd()
    output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
    logger.debug(f"Output directory: {output_dir}, template: {output_template}")

    try:
        logger.info("Initializing yt-dlp downloader")
        with yt_dlp.YoutubeDL(
            {  # options
                "format": "best",
                "outtmpl": output_template,
                "noplaylist": True,
                "quiet": True,
                "progress_hooks": [progress],
            }
        ) as ydl:
            logger.info("Extracting video info and downloading")
            info_dict = ydl.extract_info(video_url, download=True)
            if "filepath" in info_dict:
                filepath = info_dict["filepath"]
                logger.info(f"Video downloaded successfully to: {filepath}")
                return filepath
            else:
                file_name = ydl.prepare_filename(info_dict)
                filepath = os.path.join(output_dir, file_name)
                logger.info(f"Video downloaded successfully to: {filepath}")
                return filepath
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        return None


def extract_audio(video_path):
    logger.info(f"Starting audio extraction from video: {video_path}")
    output_path = f"{video_path}.wav"
    logger.debug(f"Output audio path: {output_path}")

    cmd = f"ffmpeg -i '{video_path}' -ab 160k -ac 2 -ar 44100 -vn {output_path} -y"
    logger.info(f"Running ffmpeg command: {cmd}")

    try:
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
        logger.info(f"Audio extraction completed successfully: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Audio extraction failed with exit code {e.returncode}")
        raise


def transcribe(filename, model):
    logger.info(f"Starting transcription for file: {filename} using model: {model}")

    try:
        logger.info("Loading audio file")
        audio = whisper.load_audio(filename)
        logger.info("Audio loaded successfully")

        logger.info(f"Loading Whisper model: {model}")
        model = whisper.load_model(model, device="cpu")
        logger.info("Whisper model loaded successfully")

        logger.info("Starting transcription process")
        result = whisper.transcribe(model, audio)
        logger.info(f"Transcription completed. Found {len(result['segments'])} segments")

        return result
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise


class LLMClipFinder:
    """Class to handle LLM API calls for identifying interesting clips"""

    def __init__(self, api_key=None, model="gemini-2.5-flash"):
        """Initialize with optional API key (for Google Gemini)"""
        logger.info(f"Initializing LLMClipFinder with model: {model}")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model

        if not self.api_key:
            logger.warning("No Google Gemini API key found. Falling back to alternate method.")
            self.use_gemini = False
            return

        # Configure the Gemini API client
        try:
            logger.info("Configuring Gemini API client")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.use_gemini = True
            logger.info("Gemini API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self.use_gemini = False

    def find_interesting_moments(self, user_prompt, transcription_segments, min_clips=3, max_clips=10):
        """Use LLM to identify interesting moments from transcription segments"""
        logger.info(f"Finding interesting moments with prompt: '{user_prompt}'")
        logger.info(f"Processing {len(transcription_segments)} transcription segments")

        # Format the transcription data for the LLM
        logger.debug("Formatting transcription data for LLM")
        transcript_text = ""
        for _, segment in enumerate(transcription_segments):
            start_time = self._format_time(segment["start"])
            end_time = self._format_time(segment["end"])
            transcript_text += f"[{start_time} - {end_time}] {segment['text']}\n"

        # Create prompt for the LLM
        prompt = f"""
You are an expert video editor who finds the most compelling moments in videos.

Here's a transcript with timestamps:

{transcript_text}

Please identify {min_clips}-{max_clips} moments that would make {user_prompt} great short clips (arbitrary 0-60 seconds each). Focus on:
1. Interesting statements or stories
2. Emotional moments
3. Surprising revelations or insights
4. Quotable or memorable segments
5. Self-contained moments that work well in isolation
6. AND MOST IMPORTANT: {user_prompt}

Format your response as JSON with this structure:
{{
  "clips": [
    {{
      "start": "mm:ss",
      "end": "mm:ss",
      "reason": "brief explanation",
      "caption": "suggested caption"
    }},
    ...
  ]
}}
"""

        if self.use_gemini:
            logger.info("Using Gemini API for clip finding")
            return self._call_gemini_api(prompt)
        else:
            logger.info("Using fallback extraction method")
            return self._fallback_extraction(transcription_segments)

    def _call_gemini_api(self, prompt):
        """Call Gemini API with proper error handling"""
        logger.info("Calling Gemini API")
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            logger.debug("Gemini API call successful")

            # Try to parse the JSON from the response
            try:
                # Find JSON in the response if it's not pure JSON
                import re

                json_match = re.search(r"\{[\s\S]*\}", content)
                if json_match:
                    content = json_match.group(0)

                import json

                clip_data = json.loads(content)
                return clip_data
            except json.JSONDecodeError:
                print("Failed to parse JSON from LLM response. Using manual extraction.")
                return self._manually_extract_clips(content)

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            logger.info("Falling back to manual extraction")
            return self._fallback_extraction(self.transcription_segments)

    def _manually_extract_clips(self, content):
        """Manually extract clip information if JSON parsing fails"""
        clips = []

        # Try to find and extract clip information using regex
        import re

        # Look for patterns like "Start: 01:23" or "Start time: 01:23"
        start_times = re.findall(r"start(?:\s+time)?:\s*(\d+:\d+)", content, re.IGNORECASE)
        end_times = re.findall(r"end(?:\s+time)?:\s*(\d+:\d+)", content, re.IGNORECASE)

        # Extract everything between "Reason:" and the next section as the reason
        reasons = re.findall(
            r"reason:\s*(.*?)(?=\n\s*(?:caption|start|end|clip|\d+\.)|\Z)", content, re.IGNORECASE | re.DOTALL
        )

        # Extract captions
        captions = re.findall(
            r"caption:\s*(.*?)(?=\n\s*(?:reason|start|end|clip|\d+\.)|\Z)", content, re.IGNORECASE | re.DOTALL
        )

        # Match up the extracted information
        for i in range(min(len(start_times), len(end_times))):
            clip = {
                "start": start_times[i],
                "end": end_times[i],
                "reason": reasons[i].strip() if i < len(reasons) else "Interesting moment",
                "caption": captions[i].strip() if i < len(captions) else "Check out this moment!",
            }
            clips.append(clip)

        return {"clips": clips}

    def _fallback_extraction(self, transcription_segments):
        """Simple fallback method if all API calls fail"""
        clips = []

        # Group segments into potential clips (simple approach)
        # This is a very basic fallback that just picks evenly spaced segments
        total_segments = len(transcription_segments)
        num_clips = min(5, total_segments // 3)  # Create up to 5 clips

        if num_clips == 0 and total_segments > 0:
            num_clips = 1

        for i in range(num_clips):
            idx = (i * total_segments) // num_clips
            segment = transcription_segments[idx]

            # Calculate clip start/end (aim for 45-60 second clips)
            clip_mid = (segment["start"] + segment["end"]) / 2
            clip_start = max(0, clip_mid - 25)
            clip_end = min(clip_mid + 25, segment["end"] + 30)

            clip = {
                "start": self._format_time(clip_start),
                "end": self._format_time(clip_end),
                "reason": "Potentially interesting segment",
                "caption": segment["text"][:100] + "..." if len(segment["text"]) > 100 else segment["text"],
            }
            clips.append(clip)

        return {"clips": clips}

    def _format_time(self, seconds):
        """Format seconds to mm:ss format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
