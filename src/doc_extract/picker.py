"""Интерактивный выбор файлов в терминале."""

from pathlib import Path

import questionary

from doc_extract.scanner import Candidate, output_path

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


def pick_directory(default: Path) -> Path | None:
    """Ввод каталога с автодополнением (Tab); None при отмене."""

    def validate(text: str) -> bool | str:
        return Path(text).expanduser().is_dir() or "Нет такого каталога"

    answer = questionary.path(
        "Каталог с файлами (Tab — дополнение, Enter — подтвердить):",
        default=str(default),
        only_directories=True,
        validate=validate,
    ).ask()
    return Path(answer).expanduser().resolve() if answer else None


def pick(candidates: list[Candidate], preselected: set[str] = frozenset()) -> list[Path]:
    """Чекбокс-список; возвращает выбранные пути (пусто при отмене).

    Файлы с именами из preselected отмечены заранее.
    """
    selected = questionary.checkbox(
        "Выберите файлы для извлечения текста "
        "(пробел — отметить, a — все, i — инвертировать, Enter — готово):",
        choices=[
            questionary.Choice(choice_title(c), value=c.path, checked=c.path.name in preselected)
            for c in candidates
        ],
    ).ask()
    return selected or []


def confirm_overwrite(paths: list[Path]) -> bool:
    names = ", ".join(output_path(p).name for p in paths)
    return bool(questionary.confirm(f"Перезаписать существующие: {names}?", default=False).ask())
