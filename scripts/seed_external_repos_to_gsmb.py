"""
Script: seed_external_repos_to_gsmb.py
Purpose: Harvest core architecture, governance specs, and contracts from external estate checkouts
         on C:\\Users\\rkhol\\ directly into the local GSMB vault.
Rule: "The stronger should be local. Everything needs to come to local."
Authority: Master Robyn Kholofelo Rababalela (Seat 1)
Compiler: AntiGravity (Seat 10)
"""

import os
import shutil
import json
import time
from pathlib import Path

BASE_DIR = Path(r"C:\Users\rkhol")
GSMB_LOCAL_ROOT = Path(r"c:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP")
SEED_TARGET_DIR = GSMB_LOCAL_ROOT / "Schematics" / "21-KOPANO-PHU GOVERNACE SYSTEMS" / "MAIN-BRAIN" / "External-Estate-Seeds"

REPOS_TO_SEED = [
    {
        "name": "Project-Jennifer",
        "path": BASE_DIR / "Project-Jennifer",
        "key_files": [
            "Project_Jennifer.md",
            "VALIDATION_POLICY.md",
            "VALIDATION_FAILED.md",
            "PERN_ROADMAP.md",
            "NCMP.md",
            "package.json"
        ]
    },
    {
        "name": "KMEC-Morning-Engine",
        "path": BASE_DIR / "kpgs-morning-engine-core--kmec-",
        "key_files": [
            "README.md",
            "package.json",
            "requirements.txt"
        ]
    },
    {
        "name": "Partial-Knowable-Algebra",
        "path": BASE_DIR / "Partial-Knowable-Algebra",
        "key_files": [
            "README.md"
        ]
    },
    {
        "name": "Search-Entity-Architecture",
        "path": BASE_DIR / "Search-Entity-Architecture",
        "key_files": [
            "README.md"
        ]
    },
    {
        "name": "Cars4Mars-Project",
        "path": BASE_DIR / "cars4mars-project",
        "key_files": [
            "README.md",
            "requirements.txt"
        ]
    },
    {
        "name": "Cars4Mars-LandingPage",
        "path": BASE_DIR / "cars4mars-landingpage",
        "key_files": [
            "README.md",
            "package.json"
        ]
    },
    {
        "name": "CrisisConnect-Dispatch",
        "path": BASE_DIR / "crisis-connect",
        "key_files": [
            "README.md",
            "package.json"
        ]
    },
    {
        "name": "Paws-and-Potjie",
        "path": BASE_DIR / "paws-and-potjie",
        "key_files": [
            "README.md",
            "package.json"
        ]
    },
    {
        "name": "Kopano-Labs-Interns",
        "path": BASE_DIR / "Kopano-Labs-Interns",
        "key_files": [
            "README.md",
            "package.json"
        ]
    },
    {
        "name": "Amaphu-App",
        "path": BASE_DIR / "amaphu-app",
        "key_files": [
            "README.md",
            "package.json"
        ]
    },
    {
        "name": "Ayakha-AI",
        "path": BASE_DIR / "ayakha-ai",
        "key_files": [
            "README.md"
        ]
    },
    {
        "name": "Kopano-Labs-Website",
        "path": BASE_DIR / "Kopano-Labs-Website",
        "key_files": [
            "README.md",
            "package.json"
        ]
    }
]


def execute_seeding():
    print(f"=== GSMB HEAVY SEEDING INGESTION ===")
    print(f"Target: {SEED_TARGET_DIR}")
    SEED_TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "compiler": "AntiGravity (Seat 10 / Chief Facilitator)",
        "seeded_repositories": []
    }

    total_files_seeded = 0

    for repo in REPOS_TO_SEED:
        repo_name = repo["name"]
        repo_path = repo["path"]
        target_repo_dir = SEED_TARGET_DIR / repo_name
        
        if not repo_path.exists():
            print(f"[-] SKIPPED: {repo_name} (path not found: {repo_path})")
            continue
            
        target_repo_dir.mkdir(parents=True, exist_ok=True)
        seeded_items = []
        
        # Check git commit
        git_head = "UNKNOWN"
        git_head_file = repo_path / ".git" / "HEAD"
        if git_head_file.exists():
            try:
                head_ref = git_head_file.read_text().strip()
                if head_ref.startswith("ref:"):
                    ref_path = repo_path / ".git" / head_ref.split()[1]
                    if ref_path.exists():
                        git_head = ref_path.read_text().strip()
                else:
                    git_head = head_ref
            except Exception as e:
                git_head = f"ERROR: {e}"

        for kf in repo["key_files"]:
            src = repo_path / kf
            if src.exists() and src.is_file():
                dest = target_repo_dir / kf
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                seeded_items.append(kf)
                total_files_seeded += 1
                
        print(f"[+] SEEDED: {repo_name} | HEAD: {git_head[:8]} | Files: {len(seeded_items)}")
        
        manifest["seeded_repositories"].append({
            "repository": repo_name,
            "source_path": str(repo_path),
            "git_head": git_head,
            "files": seeded_items
        })

    manifest_path = SEED_TARGET_DIR / "SEED_INGESTION_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nSeeding complete! {total_files_seeded} files ingested into GSMB Local.")
    print(f"Manifest written to: {manifest_path}")


if __name__ == "__main__":
    execute_seeding()
