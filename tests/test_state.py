from doc_extract import state


def test_load_missing_returns_empty():
    assert state.load() == state.LastSelection()


def test_save_and_load_roundtrip(tmp_path):
    (tmp_path / "Отчёт.pdf").write_text("x")
    state.save(tmp_path, [tmp_path / "Отчёт.pdf"])
    last = state.load()
    assert last.directory == tmp_path.resolve()
    assert last.files == {"Отчёт.pdf"}


def test_corrupted_state_ignored():
    path = state.state_file()
    path.parent.mkdir(parents=True)
    path.write_text("{not json")
    assert state.load() == state.LastSelection()
