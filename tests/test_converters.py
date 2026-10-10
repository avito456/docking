from docling_core.types.doc import DocItemLabel, DoclingDocument
from docling_core.types.doc.document import TrackSource

from doc_extract.converters import join_segments


def test_join_segments_merges_until_pause():
    doc = DoclingDocument(name="x")
    for text, start, end in [(" Привет.", 0, 1), (" Как дела?", 1.2, 2), (" Новая мысль.", 5, 6)]:
        doc.add_text(label=DocItemLabel.TEXT, text=text, source=TrackSource(start_time=start, end_time=end))

    assert join_segments(doc) == "Привет. Как дела?\n\nНовая мысль."


def test_convert_writes_transcript_md(tmp_path, monkeypatch):
    from doc_extract.converters import Extractor

    src = tmp_path / "report.pdf"
    src.write_text("x")
    ext = Extractor.__new__(Extractor)
    monkeypatch.setattr(Extractor, "to_markdown", lambda self, path: "# Привет")

    out = ext.convert(src)

    assert out == tmp_path / "report_transcript.md"
    assert out.read_text(encoding="utf-8") == "# Привет"
    assert not (tmp_path / "report.md").exists()
