# doc-extract

Извлечение текста из документов (Word, Excel, PDF) и транскрибация аудио/видео в Markdown.
Работает на [docling](https://github.com/docling-project/docling); речь распознаётся Whisper через MLX
(ускорение на GPU Apple Silicon M1/M2/M3).

## Установка

```bash
brew install ffmpeg      # нужен для видео
uv sync
```

При первом запуске docling скачает модели (layout/OCR для PDF и whisper-turbo ~1.5 ГБ) в `~/.cache/huggingface`.

Или
~~~sh
HF_HUB_DISABLE_XET=1 uv run python -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/whisper-turbo')"
~~~

## Использование

Из папки проекта:

```bash
uv run extract                         # диалог: выбор папки, затем файлов
uv run extract ~/Documents/inbox       # диалог по файлам указанной папки
uv run extract report.pdf call.m4a     # обработать файлы без диалога
```

Из любой папки с файлами:

```bash
uv run --project ~/workspace/docling extract
# или установить как команду:
uv tool install ~/workspace/docling && extract
```

Без аргументов сначала спрашивается папка (Tab — автодополнение пути, Enter — подтвердить).
По умолчанию подставляется папка из прошлого запуска, а файлы, выбранные в прошлый раз, уже отмечены.
Последний выбор хранится в `~/.config/doc-extract/state.json` (или `$XDG_CONFIG_HOME/doc-extract/state.json`).

В диалоге выбора файлов: стрелки — перемещение, пробел — отметить, `a` — выбрать все, `i` — инвертировать, Enter — запуск.
Файлы, для которых уже есть `.md`, помечены `[md есть]`.

Результат сохраняется рядом с исходником: `report.pdf` → `report.md`.

### Параметры

| Флаг | Описание |
|---|---|
| `--model {tiny,base,small,medium,large,turbo}` | модель Whisper (по умолчанию `turbo`) |
| `--language ru` | язык аудио (по умолчанию — автоопределение) |
| `--force` | перезаписывать существующие `.md` без вопроса |

## Форматы

| Тип | Расширения |
|---|---|
| Word | `.docx` |
| Excel | `.xlsx`, `.xls` |
| PDF | `.pdf` (сканы распознаются OCR) |
| Аудио | `.mp3 .wav .m4a .flac .ogg .aac` |
| Видео | `.mp4 .mov .mkv .avi .webm` (аудиодорожка извлекается ffmpeg) |

Старый формат `.doc` не поддерживается — пересохраните файл в `.docx`.

## Тесты

```bash
uv run pytest
```
