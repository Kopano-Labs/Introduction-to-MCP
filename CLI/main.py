import asyncio
import sys
import os
import multiprocessing
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude

from core.cli_chat import CliChat
from core.cli import CliApp

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- PYINSTALLER SUBPROCESS ROUTER ---
if "--mcp-server" in sys.argv:
    mcp_server_path = os.path.join(BASE_DIR, "mcp_server.py")
    with open(mcp_server_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, {"__name__": "__main__", "__file__": mcp_server_path})
    sys.exit(0)
# -------------------------------------

# Anthropic Config
claude_model = os.getenv("CLAUDE_MODEL", "")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")


assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert anthropic_api_key, (
    "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
)


async def main():
    claude_service = Claude(model=claude_model)

    server_scripts = [arg for arg in sys.argv[1:] if arg != "--mcp-server"]
    clients = {}

    mcp_server_path = os.path.join(BASE_DIR, "mcp_server.py")
    
    if getattr(sys, 'frozen', False):
        command = sys.executable
        args = ["--mcp-server"]
    else:
        command = "uv" if os.getenv("USE_UV", "0") == "1" else sys.executable
        args = ["run", mcp_server_path] if command == "uv" else [mcp_server_path]

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=claude_service,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


def cli_entry():
    asyncio.run(main())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    cli_entry()
