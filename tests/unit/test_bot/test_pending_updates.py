"""Messages sent while the bot is down are kept, not dropped on restart."""

import ast
from pathlib import Path

import src.bot.core as core


def test_pending_updates_never_dropped():
    """Every drop_pending_updates argument in the bot's start-up is False."""
    tree = ast.parse(Path(core.__file__).read_text(encoding="utf-8"))
    values = [
        kw.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        for kw in node.keywords
        if kw.arg == "drop_pending_updates"
    ]
    assert values == [False, False]
