import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude

from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# Anthropic Config
claude_model = os.getenv("CLAUDE_MODEL", "")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")


assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert anthropic_api_key, (
    "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
)


async def main():
    claude_service = Claude(model=claude_model)

    server_scripts = sys.argv[1:]
    clients = {}

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        # --- TEST: List available tools ---
        print("--- Testing list_tools ---")
        try:
            tools = await doc_client.list_tools()
            if not tools:
                print("No tools found on the server.")
            for tool in tools:
                print(f"  Tool: {tool.name}")
                print(f"    Description: {tool.description}")
        except Exception as e:
            print(f"Error listing tools: {e}")
        # --- END TEST ---

        # --- TEST: Read document IDs resource ---
        print("--- Testing doc_ids resource ---")
        try:
            doc_ids = await doc_client.read_resource("resource://doc_ids")
            print(f"  Doc IDs: {doc_ids}")
        except Exception as e:
            print(f"Error reading resource: {e}")
        # --- END TEST ---

        # --- TEST: Get prompt ---
        print("--- Testing get_prompt ---")
        try:
            prompt_result = await doc_client.get_prompt("summarize_doc", {"doc_id": "plan.md"})
            print(f"  Prompt: {prompt_result}")
            print("--- Test complete, starting chat ---")
        except Exception as e:
            print(f"Error getting prompt: {e}")
        # --- END TEST ---

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


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
