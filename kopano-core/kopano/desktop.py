"""Default desktop launcher: API + bundled Kopano Studio."""

from __future__ import annotations

import os
import sys
import webbrowser


def run_desktop(
    *,
    host: str | None = None,
    port: int | None = None,
    open_browser: bool = True,
) -> None:
    from rich.console import Console
    from rich.panel import Panel

    host = host or os.environ.get("KOPANO_HOST", "127.0.0.1")
    port = int(port or os.environ.get("KOPANO_PORT", "8000"))
    url = f"http://{host}:{port}"

    console = Console()
    console.print(
        Panel(
            f"[bold green]Kopano Context[/bold green] desktop\n"
            f"Studio + API: [bold cyan]{url}[/bold cyan]\n"
            f"First launch may take ~30s while models and telemetry load.\n"
            f"Close this window to stop the server.",
            title="KopanoContext.exe",
            expand=False,
        )
    )

    if open_browser and os.environ.get("KOPANO_NO_BROWSER", "").lower() not in {"1", "true", "yes"}:
        try:
            webbrowser.open(url)
        except OSError:
            console.print("[yellow]Could not open a browser automatically.[/yellow]")

    import uvicorn

    from .api import app

    uvicorn.run(app, host=host, port=port, log_level="info")


def main() -> None:
    """CLI entry when frozen: `KopanoContext.exe` or `KopanoContext.exe serve api`."""
    argv = sys.argv[1:]
    if not argv or argv[0] in {"serve", "desktop"}:
        if argv and argv[0] == "serve":
            argv = argv[1:]
        open_browser = True
        host = "127.0.0.1"
        port = 8000
        if argv and argv[0] == "api":
            argv = argv[1:]
        i = 0
        while i < len(argv):
            token = argv[i]
            if token in {"--no-open", "--no-browser"}:
                open_browser = False
            elif token == "--host" and i + 1 < len(argv):
                host = argv[i + 1]
                i += 1
            elif token.startswith("--host="):
                host = token.split("=", 1)[1]
            elif token == "--port" and i + 1 < len(argv):
                port = int(argv[i + 1])
                i += 1
            elif token.startswith("--port="):
                port = int(token.split("=", 1)[1])
            i += 1
        run_desktop(host=host, port=port, open_browser=open_browser)
        return

    from .cli import app

    app()
