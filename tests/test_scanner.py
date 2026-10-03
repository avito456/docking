from pathlib import Path

from doc_extract.scanner import file_kind, output_path, scan


def test_file_kind():
    assert file_kind(Path("a.DOCX")) == "word"
    assert file_kind(Path("a.xlsx")) == "excel"
    assert file_kind(Path("a.pdf")) == "pdf"
    assert file_kind(Path("a.mp3")) == "audio"
    assert file_kind(Path("a.mov")) == "video"
    assert file_kind(Path("a.txt")) is None
    assert file_kind(Path("a.doc")) is None


def test_output_path():
    assert output_path(Path("/x/report.pdf")) == Path("/x/report.md")


def test_scan_filters_and_marks_existing(tmp_path):
    for name in ["b.pdf", "a.mp3", "notes.txt", ".hidden.pdf", "~$lock.docx", "b.md"]:
        (tmp_path / name).write_text("x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.pdf").write_text("x")

    found = scan(tmp_path)

    assert [c.path.name for c in found] == ["a.mp3", "b.pdf"]
    assert [c.has_output for c in found] == [False, True]
