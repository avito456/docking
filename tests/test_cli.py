from pathlib import Path

from doc_extract import cli


def test_parse_defaults():
    args = cli.parse_args([])
    assert args.paths == []
    assert args.model == "turbo"
    assert args.language is None
    assert args.force is False


def test_explicit_files_skip_dialog_and_unsupported(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.write_text("x")
    txt = tmp_path / "b.txt"
    txt.write_text("x")

    files, interactive = cli.resolve_targets(cli.parse_args([str(pdf), str(txt), str(tmp_path / "nope.pdf")]))

    assert files == [pdf]
    assert interactive is False


def test_existing_md_skipped_without_force(tmp_path, monkeypatch):
    pdf = tmp_path / "a.pdf"
    pdf.write_text("x")
    (tmp_path / "a.md").write_text("old")
    converted = []

    class FakeExtractor:
        def __init__(self, **kw):
            pass

        def convert(self, path: Path) -> Path:
            converted.append(path)
            return path.with_suffix(".md")

    monkeypatch.setattr("doc_extract.converters.Extractor", FakeExtractor)

    assert cli.main([str(pdf)]) == 0
    assert converted == []
    assert cli.main([str(pdf), "--force"]) == 0
    assert converted == [pdf]
