"""Start the bot's real Claude call on this machine with a CLAUDE.md past
Windows' 32,767-character command limit, and report how the CLI start went."""

import asyncio
import tempfile
from pathlib import Path

from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport

import src.claude.sdk_integration as sdk
from src.config.settings import Settings


async def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="probe-"))
    (work / "CLAUDE.md").write_text(
        "PROBE-MARKER\n" + "Background filler line. " * 1700, encoding="utf-8"
    )
    cfg = Settings(
        telegram_bot_token="test:token",
        telegram_bot_username="testbot",
        approved_directory=work,
        claude_timeout_seconds=90,
    )
    captured = []
    real = sdk.ClaudeSDKClient

    def spy(options, *a, **k):
        captured.append(options)
        return real(options, *a, **k)

    sdk.ClaudeSDKClient = spy
    try:
        r = await sdk.ClaudeSDKManager(cfg).execute_command(
            prompt="hello", working_directory=work
        )
        print("OUTCOME: returned", repr(r.content)[:300])
    except Exception as e:  # report, never hide
        print("OUTCOME: raised", type(e).__name__, str(e)[:500])
    if captured:
        opts = captured[0]
        opts.cli_path = opts.cli_path or "claude"
        cmd = SubprocessCLITransport(prompt="hello", options=opts)._build_command()
        print("COMMAND LENGTH:", len(" ".join(cmd)))
        print("PROMPT AS FILE:", "--system-prompt-file" in cmd)


asyncio.run(main())
