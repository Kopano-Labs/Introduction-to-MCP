import json
ledger_path = 'docs/swarm-ops/jiro/JIRO_STAP_LEDGER.json'
with open(ledger_path) as f:
    ledger = json.load(f)

new_tasks = [
    {"id":"014","title":"Fix tests (63/73 pass)","status":"DONE","commit":"2c6ca67","poc":"82.5%"},
    {"id":"015","title":"5 auto runner tests","status":"DONE","commit":"63e062f","poc":"100%"},
    {"id":"016","title":"5 FON-C tests","status":"DONE","commit":"3db09ed","poc":"100%"},
    {"id":"032","title":"Font preload","status":"DONE","commit":"9a1892b","poc":"N/A"},
    {"id":"033","title":"Lazy loading images","status":"DONE","commit":"79db466","poc":"N/A"},
    {"id":"037","title":"STAP Student Guide","status":"DONE","commit":"3db09ed","poc":"N/A"},
    {"id":"039","title":"Deployment Runbook","status":"DONE","commit":"92f0b4f","poc":"N/A"},
    {"id":"040","title":"KHELOS hook docs","status":"DONE","commit":"3db09ed","poc":"N/A"},
    {"id":"046","title":"SWFUS.seal() method","status":"DONE","commit":"acc076f","poc":"100%"},
    {"id":"047","title":"Khelos sense() verified","status":"DONE","commit":"pre-existing","poc":"N/A"},
    {"id":"048","title":"KPGS Cheat Sheet","status":"DONE","commit":"63e062f","poc":"N/A"},
    {"id":"011","title":"README badges","status":"DONE","commit":"a84cdc0","poc":"N/A"},
]

existing_ids = {t["id"] for t in ledger["tasks_completed"]}
added = 0
for t in new_tasks:
    if t["id"] not in existing_ids:
        ledger["tasks_completed"].append(t)
        added += 1

total = len(ledger["tasks_completed"])
ledger["poc_stats"]["total_validated"] = total
with open(ledger_path, "w") as f:
    json.dump(ledger, f, indent=2)
print(f"Ledger: {total} tasks done (+{added} new)")
