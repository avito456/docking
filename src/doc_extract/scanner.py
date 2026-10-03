"""Поиск поддерживаемых файлов и определение их типа."""

from dataclasses import dataclass
from pathlib import Path

KINDS: dict[str, set[str]] = {
    "word": {".docx"},
    "excel": {".xlsx", ".xls"},
    "pdf": {".pdf"},
    "audio": {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"},
    "video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
}

SUPPORTED_EXTENSIONS: set[str] = set().union(*KINDS.values())


def file_kind(path: Path) -> str | None:
    ext = path.suffix.lower()
    for kind, exts in KINDS.items():
        if ext in exts:
            return kind
    return None


def output_path(path: Path) -> Path:
    return path.with_suffix(".md")


@dataclass(frozen=True)
class Candidate:
    path: Path
    kind: str

    @property
    def has_output(self) -> bool:
        return output_path(self.path).exists()


def scan(directory: Path) -> list[Candidate]:
    """Поддерживаемые файлы в папке (без рекурсии), отсортированные по имени."""
    result = []
    for p in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if not p.is_file() or p.name.startswith((".", "~$")):
            continue
        kind = file_kind(p)
        if kind:
            result.append(Candidate(p, kind))
    return result
