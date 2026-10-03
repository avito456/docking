"""Извлечение аудиодорожки из видео через ffmpeg."""

import shutil
import subprocess
from pathlib import Path


class MediaError(RuntimeError):
    pass


def extract_audio(video: Path, out_dir: Path) -> Path:
    """Сохраняет аудио из видео в mono WAV 16 кГц (формат, который ожидает Whisper)."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MediaError("ffmpeg не найден. Установите: brew install ffmpeg")
    wav = out_dir / f"{video.stem}.wav"
    proc = subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-i", str(video),
         "-vn", "-ac", "1", "-ar", "16000", str(wav)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise MediaError(f"ffmpeg: {proc.stderr.strip() or 'не удалось извлечь аудио'}")
    return wav
