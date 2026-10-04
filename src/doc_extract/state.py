"""Запоминание последнего выбранного каталога и файлов между запусками."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


def state_file() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "doc-extract" / "state.json"


@dataclass
class LastSelection:
    directory: Path | None = None
    files: set[str] = field(default_factory=set)  # имена файлов внутри directory


def load() -> LastSelection:
    try:
        data = json.loads(state_file().read_text(encoding="utf-8"))
        directory = Path(data["directory"])
        files = {str(name) for name in data.get("files", [])}
    except (OSError, ValueError, KeyError, TypeError):
        return LastSelection()
    return LastSelection(directory, files)


def save(directory: Path, files: list[Path]) -> None:
    path = state_file()
    data = {
        "directory": str(directory.resolve()),
        "files": sorted(f.name for f in files),
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass  # не удалось сохранить — не повод прерывать обработку
