"""Default desktop launcher: API + bundled Kopano Studio (native window or browser)."""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

from .runtime import is_frozen_runtime, user_data_dir

logger = logging.getLogger("kopano.desktop")


def _configure_desktop_logging() -> None:
    if not is_frozen_runtime():
        return
    logs = user_data_dir() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    log_file = logs / "desktop.log"
    if not logging.getLogger().handlers:
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )


def wait_for_server(url: str, *, timeout_seconds: float = 120.0, interval: float = 0.4) -> bool:
    """Poll until the API responds (any HTTP status except connection errors)."""
    health_url = url.rstrip("/") + "/health"
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=2) as response:
                if 200 <= response.status < 500:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(interval)
    return False


def start_api_server(*, host: str, port: int) -> tuple[threading.Thread, object]:
    import uvicorn

    from .api import app

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, name="kopano-api", daemon=True)
    thread.start()
    return thread, server


def open_native_window(*, title: str, url: str, width: int = 1440, height: int = 920) -> bool:
    try:
        import webview
    except ImportError:
        logger.warning("pywebview not installed; falling back to system browser")
        return False

    window = webview.create_window(
        title,
        url,
        width=width,
        height=height,
        min_size=(1024, 720),
        text_select=True,
    )
    webview.start()
    return True


def run_desktop(
    *,
    host: str | None = None,
    port: int | None = None,
    open_browser: bool = True,
    use_native_window: bool | None = None,
) -> None:
    from rich.console import Console
    from rich.panel import Panel

    _configure_desktop_logging()

    host = host or os.environ.get("KOPANO_HOST", "127.0.0.1")
    port = int(port or os.environ.get("KOPANO_PORT", "8000"))
    base_url = f"http://{host}:{port}"
    studio_url = f"{base_url}/#/training"

    if use_native_window is None:
        env_window = os.environ.get("KOPANO_NATIVE_WINDOW", "").lower()
        if env_window in {"0", "false", "no"}:
            use_native_window = False
        elif env_window in {"1", "true", "yes"}:
            use_native_window = True
        else:
            use_native_window = is_frozen_runtime()

    console = Console()
    if not use_native_window or not is_frozen_runtime():
        console.print(
            Panel(
                f"[bold green]Kopano Context[/bold green] desktop\n"
                f"Studio + API: [bold cyan]{base_url}[/bold cyan]\n"
                f"User UI: [bold cyan]{base_url}/#/training[/bold cyan]\n"
                f"Admin: [bold cyan]{base_url}/#/admin[/bold cyan]\n"
                f"First launch may take ~30s while models and telemetry load.",
                title="KopanoContext",
                expand=False,
            )
        )

    thread, server = start_api_server(host=host, port=port)
    if not wait_for_server(base_url):
        console.print("[bold red]Timed out waiting for the local API.[/bold red]")
        server.should_exit = True
        thread.join(timeout=5)
        raise SystemExit(1)

    if not open_browser and not use_native_window:
        console.print("[yellow]Server running headless. Press Ctrl+C to stop.[/yellow]")
        try:
            while thread.is_alive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        server.should_exit = True
        return

    opened = False
    if use_native_window:
        opened = open_native_window(title="Kopano Context", url=studio_url)
        server.should_exit = True
        thread.join(timeout=10)
        return

    if open_browser and os.environ.get("KOPANO_NO_BROWSER", "").lower() not in {"1", "true", "yes"}:
        try:
            webbrowser.open(studio_url)
            opened = True
        except OSError:
            console.print("[yellow]Could not open a browser automatically.[/yellow]")

    if opened:
        console.print("[dim]Close this window or press Ctrl+C to stop the server.[/dim]")
        try:
            while thread.is_alive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        server.should_exit = True
        return

    # Blocking serve (legacy dev path)
    import uvicorn

    from .api import app

    server.should_exit = True
    thread.join(timeout=2)
    uvicorn.run(app, host=host, port=port, log_level="info")


def main() -> None:
    """CLI entry when frozen: `KopanoContext.exe` or `KopanoContext.exe serve api`."""
    argv = sys.argv[1:]
    if not argv or argv[0] in {"serve", "desktop"}:
        if argv and argv[0] == "serve":
            argv = argv[1:]
        open_browser = True
        use_native_window: bool | None = None
        host = "127.0.0.1"
        port = 8000
        if argv and argv[0] == "api":
            argv = argv[1:]
        i = 0
        while i < len(argv):
            token = argv[i]
            if token in {"--no-open", "--no-browser"}:
                open_browser = False
            elif token == "--no-window":
                use_native_window = False
            elif token == "--window":
                use_native_window = True
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
        run_desktop(
            host=host,
            port=port,
            open_browser=open_browser,
            use_native_window=use_native_window,
        )
        return

    from .cli import app

    app()
