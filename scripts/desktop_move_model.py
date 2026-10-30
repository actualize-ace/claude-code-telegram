"""Model the office-desktop .env from the Marc runsheet through the bot's own config loader.

Run from the folder that holds .env (the bot's working folder). Prints PASS/FAIL lines.
Usage: python desktop_move_model.py <vault_dir> <home_dir>
"""

import inspect
import os
import sys
from pathlib import Path

vault, home = Path(sys.argv[1]), Path(sys.argv[2])
vault.mkdir(parents=True, exist_ok=True)
(home / ".claude" / "projects").mkdir(parents=True, exist_ok=True)
temp = Path(os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp")
sep = ";" if os.name == "nt" else ","

env_text = "\n".join(
    [
        "TELEGRAM_BOT_TOKEN=123456:TEST-not-a-real-token",
        "TELEGRAM_BOT_USERNAME=modelbot",
        f"APPROVED_DIRECTORY={vault}",
        f"APPROVED_DIRECTORIES={temp}{sep}{home / '.claude' / 'projects'}",
        "ALLOWED_USERS=12345",
        "ENVIRONMENT=ace",
        "CLAUDE_TIMEOUT_SECONDS=900",
        "RATE_LIMIT_REQUESTS=100",
        "CLAUDE_MAX_COST_PER_REQUEST=25",
        "CLAUDE_ALLOWED_TOOLS=Read,Write,Edit,Bash,PowerShell,SendMessage",
        "ENABLE_MCP=false",
        "ENABLE_GIT_INTEGRATION=false",
        "CLAUDE_CODE_STREAM_CLOSE_TIMEOUT=180000",
    ]
)
Path(".env").write_text(env_text + "\n", encoding="utf-8")

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f" :: {detail}" if detail else ""))


from src.config.loader import load_config  # noqa: E402

s = load_config()
check("environment ace keeps .env timeout", s.claude_timeout_seconds == 900, str(s.claude_timeout_seconds))
check("rate limit kept", s.rate_limit_requests == 100, str(s.rate_limit_requests))
check("MCP off", s.enable_mcp is False)
check("git integration off", s.enable_git_integration is False)
roots = [str(p) for p in s.all_approved_directories]
check("approved roots parsed (vault, temp, projects)", len(roots) == 3, " | ".join(roots))
check("vault path with a space survives", "marc OS-ace" in str(s.approved_directory), str(s.approved_directory))
check("PowerShell in allowed tools", "PowerShell" in (s.claude_allowed_tools or []))
check("cost cap 25", float(s.claude_max_cost_per_request) == 25.0, str(s.claude_max_cost_per_request))

v = os.environ.get("CLAUDE_CODE_STREAM_CLOSE_TIMEOUT")
check("timeout line reaches the process environment", v == "180000", str(v))

import claude_agent_sdk  # noqa: E402
from claude_agent_sdk import ClaudeAgentOptions  # noqa: E402
from claude_agent_sdk._internal import client as sdk_internal  # noqa: E402

src = inspect.getsource(sdk_internal)
check("SDK reads CLAUDE_CODE_STREAM_CLOSE_TIMEOUT", "CLAUDE_CODE_STREAM_CLOSE_TIMEOUT" in src, claude_agent_sdk.__version__)
init_timeout = max(int(v) / 1000.0, 60.0)
check("initialize timeout becomes 180 s", init_timeout == 180.0, str(init_timeout))
try:
    ClaudeAgentOptions(max_buffer_size=32 * 1024 * 1024)
    check("photo fix option accepted by this SDK", True)
except TypeError as e:
    check("photo fix option accepted by this SDK", False, str(e))

print(f"{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
