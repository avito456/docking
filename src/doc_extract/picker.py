"""Интерактивный выбор файлов в терминале."""

from pathlib import Path

import questionary

from doc_extract.scanner import Candidate

KIND_LABELS = {
    "word": "Word",
    "excel": "Excel",
    "pdf": "PDF",
    "audio": "Аудио",
    "video": "Видео",
}


def choice_title(c: Candidate) -> str:
    mark = "  [md есть]" if c.has_output else ""
    return f"{KIND_LABELS[c.kind]:<6} {c.path.name}{mark}"


def pick(candidates: list[Candidate]) -> list[Path]:
    """Чекбокс-список; возвращает выбранные пути (пусто при отмене)."""
    selected = questionary.checkbox(
        "Выберите файлы для извлечения текста "
        "(пробел — отметить, a — все, i — инвертировать, Enter — готово):",
        choices=[questionary.Choice(choice_title(c), value=c.path) for c in candidates],
    ).ask()
    return selected or []


def confirm_overwrite(paths: list[Path]) -> bool:
    names = ", ".join(p.with_suffix(".md").name for p in paths)
    return bool(questionary.confirm(f"Перезаписать существующие: {names}?", default=False).ask())
