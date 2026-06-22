import subprocess, json
r = subprocess.run(["gh", "api", "repos/Kopano-Labs/Introduction-to-MCP/dependabot/alerts?state=open&per_page=30"], capture_output=True, text=True)
alerts = json.loads(r.stdout)
print(f"Total open alerts: {len(alerts)}")
for a in alerts:
    pkg = a["security_vulnerability"]["package"]["name"]
    sev = a.get("severity") or a["security_vulnerability"].get("severity", "?")
    fix = a["security_vulnerability"].get("first_patched_version", {})
    fix_ver = fix.get("identifier", "N/A") if fix else "N/A"
    eco = a["security_vulnerability"]["package"]["ecosystem"]
    num = a["number"]
    print(f"  #{num} | {sev.upper()} | {eco}/{pkg} | fix→{fix_ver}")

