import pytest


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Не трогать настоящий ~/.config при тестах."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
