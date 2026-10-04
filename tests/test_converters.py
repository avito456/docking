from docling_core.types.doc import DocItemLabel, DoclingDocument
from docling_core.types.doc.document import TrackSource

from doc_extract.converters import join_segments


def test_join_segments_merges_until_pause():
    doc = DoclingDocument(name="x")
    for text, start, end in [(" Привет.", 0, 1), (" Как дела?", 1.2, 2), (" Новая мысль.", 5, 6)]:
        doc.add_text(label=DocItemLabel.TEXT, text=text, source=TrackSource(start_time=start, end_time=end))

    assert join_segments(doc) == "Привет. Как дела?\n\nНовая мысль."
