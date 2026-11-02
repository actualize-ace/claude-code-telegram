"""The file handler creates its temp folder even when the parent is missing."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.bot.features import file_handler


def test_temp_dir_created_with_missing_parent(tmp_path):
    target = tmp_path / "tmp" / "claude_bot_files"
    assert not target.parent.exists()
    real_path = Path

    def fake_path(*args, **kwargs):
        if args and args[0] == "/tmp/claude_bot_files":
            return target
        return real_path(*args, **kwargs)

    with patch.object(file_handler, "Path", side_effect=fake_path):
        file_handler.FileHandler(MagicMock(), MagicMock())

    assert target.is_dir()
