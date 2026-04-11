"""
check_atlas.py — Kopano Context | Atlas Connectivity Verification
-----------------------------------------------------------------
Verifies that the MongoDB Atlas cluster (Orch) is reachable and that
the KasiLink database collections are accessible before Demo Day.

This script is scoped to the Kopano Context / KasiLink stack specifically.
It checks the Orch cluster, lists the collections Claude and KasiLink use,
and reports the connection state without reading or modifying any data.

Run:
    python scripts/check_atlas.py

Install dependency if missing:
    pip install pymongo python-dotenv
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    print("❌  MONGODB_URI not found in environment.")
    print("    Check your .env file at the project root.")
    sys.exit(1)

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure
except ImportError:
    print("❌  pymongo not installed. Run:  pip install pymongo python-dotenv")
    sys.exit(1)

# --- Kopano Context database targets ---
# KasiLink uses these databases. Update if namespace changes.
DATABASES_TO_CHECK = ["kasilink", "kopano"]

print("=" * 60)
print("  Kopano Context — Atlas Connectivity Check")
print("  Cluster: Orch @ d9trndm.mongodb.net")
print("=" * 60)
print()

client = None
exit_code = 0

try:
    print("[*]  Connecting to Atlas cluster...")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=6000)

    # Lightweight ping — no data read, just proves the server responded
    client.admin.command("ping")
    print("✅  Atlas ping: OK — cluster is reachable\n")

    # Check each database used by the Kopano ecosystem
    for db_name in DATABASES_TO_CHECK:
        try:
            db = client[db_name]
            collections = db.list_collection_names()
            if collections:
                print(f"📦  Database '{db_name}': {len(collections)} collection(s) found")
                for c in collections:
                    print(f"      • {c}")
            else:
                print(f"📦  Database '{db_name}': exists but no collections yet (empty)")
        except OperationFailure as op_err:
            # OperationFailure here means auth succeeded but this DB is restricted
            print(f"⚠️   Database '{db_name}': access denied — {op_err.details.get('errmsg', op_err)}")
            exit_code = 1

    print()
    print("=" * 60)
    if exit_code == 0:
        print("✅  ATLAS READY — all checks passed")
        print("    Safe to run demo route and KasiLink auth flow.")
    else:
        print("⚠️   ATLAS PARTIALLY READY — see warnings above")
        print("    Check Atlas Network Access if collections are inaccessible.")
    print("=" * 60)

    print()
    print("💡  Atlas IP Allowlist reminder:")
    print("    Dashboard → Security → Network Access → Add Current IP")
    print("    For Demo Day mobility: temporarily add 0.0.0.0/0")
    print("    Remove after the demo.")

except ConnectionFailure as err:
    print(f"❌  Connection failed: {err}")
    print()
    print("    Likely causes:")
    print("    1. Your current IP is not on the Atlas Network Access allowlist")
    print("       → Atlas dashboard → Security → Network Access → Add IP")
    print("    2. The Orch cluster is paused")
    print("       → Atlas dashboard → Database → Resume cluster")
    print("    3. Wrong MONGODB_URI in .env")
    exit_code = 1

finally:
    if client:
        client.close()

sys.exit(exit_code)
