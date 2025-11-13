# Mermaid diagram for my reference

```mermaid
graph TD
    A[Input dan Pengunduhan Video] -->|Masukkan link video, download via yt-dlp| B[Transkripsi Audio]
    B[Transkripsi Audio] -->|Gunakan Whisper untuk transkrip teks| C[Analisis dan Identifikasi Momen Viral]
    C[Analisis dan Identifikasi Momen Viral] -->|Kirim ke ChatGPT untuk deteksi gold nuggets, pertimbangkan tren viral| D[Deteksi dan Tracking Subjek]
    D[Deteksi dan Tracking Subjek] -->|Active Speaker Detection via TalkNet-ASD, fokus pada wajah/suara/gerakan| E[Editing dan Rendering Clip]
    E[Editing dan Rendering Clip] -->|Tambah caption, emoji, transisi; Gunakan FFmpeg untuk output| F[Output Clip Pendek Viral]
    subgraph Tech Stack
        G[Python Libraries: PyTorch, OpenCV, etc.]
        B -.-> G
        D -.-> G
        E -.-> G
    end
```
