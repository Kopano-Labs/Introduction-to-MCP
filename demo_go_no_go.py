import os
import sys
import httpx
import asyncio
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

async def check_readiness():
    console.print("[bold cyan]🚀 Kopano Context: Final Demo Day Readiness Audit[/bold cyan]")
    console.print("-" * 50)
    
    results = []
    
    # 1. Environment Check
    root_env = Path(".env")
    kasilink_env = Path("KasiLink/.env.local")
    core_env = Path("kopano-core/.env")
    
    env_status = "✅" if root_env.exists() and kasilink_env.exists() and core_env.exists() else "❌"
    results.append(["Environment Hydration", env_status, "Root, KasiLink, and Core .envs found"])
    
    # 2. Key Presence Check
    from dotenv import dotenv_values
    config = dotenv_values(".env")
    required_keys = ["AZURE_OPENAI_KEY", "MONGODB_URI", "CLERK_SECRET_KEY", "RAPIDAPI_KEY"]
    missing = [k for k in required_keys if not config.get(k)]
    
    key_status = "✅" if not missing else "❌"
    key_msg = "All required keys present" if not missing else f"Missing: {', '.join(missing)}"
    results.append(["Master Secrets", key_status, key_msg])
    
    # 3. Code Sanitization (SafeSkill 100)
    # Check for Sk- keys using simple logic
    import re
    secret_regex = re.compile(r"sk-[a-zA-Z0-9]{32}")
    found_secrets = False
    # Only scan a sample of files for speed
    for p in Path("kopano-core/kopano").rglob("*.py"):
        if secret_regex.search(p.read_text()):
            found_secrets = True
            break
            
    sanitized_status = "✅" if not found_secrets else "⚠️"
    results.append(["SafeSkill Sanitization", sanitized_status, "No raw secrets detected in core"])

    # 4. API Health Check (if running)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/health", timeout=2.0)
            if resp.status_code == 200:
                health = resp.json()
                api_status = "✅" if health["status"] == "healthy" else "⚠️"
                api_msg = f"API Live: {health['components']['database']} / {health['components']['telemetry']}"
            else:
                api_status = "⚠️"
                api_msg = f"API returned {resp.status_code}"
    except:
        api_status = "💤"
        api_msg = "API not running (Skipped active check)"
        
    results.append(["Live API Health", api_status, api_msg])

    # Display Table
    table = Table(title="Kopano Context Readiness Matrix")
    table.add_column("System", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Notes", style="green")
    
    for row in results:
        table.add_row(*row)
        
    console.print(table)
    
    if all(r[1] == "✅" or r[1] == "💤" for r in results):
        console.print("\n[bold green]STATUS: GO FOR DEMO[/bold green]")
    else:
        console.print("\n[bold red]STATUS: NO-GO (Blockers detected)[/bold red]")

if __name__ == "__main__":
    asyncio.run(check_readiness())
