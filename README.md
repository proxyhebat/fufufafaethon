# Minimal video repurposing implementation

TODOS:

- [x] Handle user inputs. For now identified inputs are YouTube Video URL, selected categories, and User Prompt.
- [ ] YouTube Downloader (using yt-dlp)
- [ ] Audio transcription, given the extracted audio from the downloaded video (ffmpeg & openai/whisper involved).
- [ ] Moments / gold-nuggets identification & analysis. For now just raw-dog to Google's Gemini AI begging for trend, viral, moment identification.
- [ ] Object, subject, and active-speaker detection (TalkNet-ASD) focusing on face, voice, and movement.
- [ ] Editing & Rendering Clips (oh shi, ffmpeg again...). For captions, emoji, filters, and transitions.
