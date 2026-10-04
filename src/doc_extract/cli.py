"""Точка входа: `uv run extract [пути...]`."""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from doc_extract import state
from doc_extract.converters import WHISPER_MODELS
from doc_extract.scanner import SUPPORTED_EXTENSIONS, file_kind, output_path, scan

console = Console()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="extract",
        description="Извлечение текста из документов и транскрибация аудио/видео в Markdown (docling).",
    )
    parser.add_argument(
        "paths", nargs="*", type=Path,
        help="Файлы для обработки или папка для выбора "
             "(без аргументов — диалог выбора папки, по умолчанию последняя использованная)",
    )
    parser.add_argument("--model", choices=WHISPER_MODELS, default="turbo",
                        help="Модель Whisper для аудио/видео (по умолчанию turbo)")
    parser.add_argument("--language", default=None,
                        help="Код языка аудио, например ru или en (по умолчанию — автоопределение)")
    parser.add_argument("--force", action="store_true", help="Перезаписывать существующие .md")
    return parser.parse_args(argv)


def resolve_targets(args: argparse.Namespace) -> tuple[list[Path], bool]:
    """Возвращает (файлы, был_ли_диалог)."""
    last = state.load()
    if len(args.paths) == 1 and args.paths[0].is_dir():
        directory = args.paths[0].resolve()
    elif args.paths:
        files = []
        for p in args.paths:
            if not p.is_file():
                console.print(f"[red]Нет такого файла:[/] {p}")
            elif file_kind(p) is None:
                console.print(f"[yellow]Пропуск (неподдерживаемый формат):[/] {p}")
            else:
                files.append(p)
        return files, False
    else:
        from doc_extract.picker import pick_directory

        default = last.directory if last.directory and last.directory.is_dir() else Path.cwd()
        directory = pick_directory(default)
        if directory is None:
            return [], True

    candidates = scan(directory)
    if not candidates:
        console.print(f"В папке [bold]{directory}[/] нет поддерживаемых файлов.\n"
                      f"Поддерживаются: {' '.join(sorted(SUPPORTED_EXTENSIONS))}")
        return [], True

    from doc_extract.picker import pick

    preselected = last.files if directory == last.directory else set()
    files = pick(candidates, preselected)
    if files:
        state.save(directory, files)
    return files, True


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    files, interactive = resolve_targets(args)
    if not files:
        if interactive:
            console.print("Ничего не выбрано.")
        return 0

    existing = [f for f in files if output_path(f).exists()]
    if existing and not args.force:
        overwrite = False
        if interactive:
            from doc_extract.picker import confirm_overwrite

            overwrite = confirm_overwrite(existing)
        if not overwrite:
            for f in existing:
                console.print(f"[yellow]Пропуск, .md уже есть:[/] {f.name} (используйте --force)")
            files = [f for f in files if f not in existing]

    from doc_extract.converters import Extractor

    extractor = Extractor(model=args.model, language=args.language)
    table = Table(title="Результат")
    table.add_column("Файл")
    table.add_column("Статус")
    table.add_column("Markdown")
    failed = 0
    for i, f in enumerate(files, 1):
        with console.status(f"[{i}/{len(files)}] {f.name} ..."):
            try:
                out = extractor.convert(f)
                table.add_row(f.name, "[green]готово[/]", str(out))
            except Exception as e:  # один сбой не останавливает остальные
                failed += 1
                table.add_row(f.name, "[red]ошибка[/]", str(e))
    if files:
        console.print(table)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
