"""Конвертация файлов в Markdown через docling."""

import tempfile
from pathlib import Path

from doc_extract.media import extract_audio
from doc_extract.scanner import file_kind, output_path

WHISPER_MODELS = ("tiny", "base", "small", "medium", "large", "turbo")


class Extractor:
    """Держит ленивые экземпляры DocumentConverter: модели грузятся один раз."""

    def __init__(self, model: str = "turbo", language: str | None = None):
        self.model = model
        self.language = language
        self._doc_converter = None
        self._asr_converter = None

    def _documents(self):
        if self._doc_converter is None:
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import DocumentConverter

            self._doc_converter = DocumentConverter(
                allowed_formats=[InputFormat.DOCX, InputFormat.XLSX, InputFormat.XLS, InputFormat.PDF]
            )
        return self._doc_converter

    def _asr(self):
        if self._asr_converter is None:
            from docling.datamodel import asr_model_specs
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import AsrPipelineOptions
            from docling.document_converter import AudioFormatOption, DocumentConverter
            from docling.pipeline.asr_pipeline import AsrPipeline

            spec = getattr(asr_model_specs, f"WHISPER_{self.model.upper()}_MLX")
            spec = spec.model_copy(update={"language": self.language})
            self._asr_converter = DocumentConverter(
                allowed_formats=[InputFormat.AUDIO],
                format_options={
                    InputFormat.AUDIO: AudioFormatOption(
                        pipeline_cls=AsrPipeline,
                        pipeline_options=AsrPipelineOptions(asr_options=spec),
                    )
                },
            )
        return self._asr_converter

    def _transcribe(self, audio: Path, title: str) -> str:
        result = self._asr().convert(audio)
        body = result.document.export_to_markdown()
        return f"# {title}\n\n_Транскрипция: whisper-{self.model} (MLX)_\n\n{body}\n"

    def to_markdown(self, path: Path) -> str:
        kind = file_kind(path)
        if kind == "audio":
            return self._transcribe(path, path.name)
        if kind == "video":
            with tempfile.TemporaryDirectory() as tmp:
                return self._transcribe(extract_audio(path, Path(tmp)), path.name)
        if kind is None:
            raise ValueError(f"Неподдерживаемый формат: {path.suffix}")
        result = self._documents().convert(path)
        return result.document.export_to_markdown()

    def convert(self, path: Path) -> Path:
        md = self.to_markdown(path)
        out = output_path(path)
        out.write_text(md, encoding="utf-8")
        return out
