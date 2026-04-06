from pathlib import Path


def test_demo_day_assets_exist():
    for path in [
        Path("DEMO_DAY_RUNBOOK.md"),
        Path("DEMO_DAY_10_PHASES_50_TASKS.md"),
        Path("scripts/demo_day_preflight.ps1"),
        Path("scripts/demo_day_readiness.py"),
        Path("scripts/demo_day_smoke.py"),
        Path("scripts/demo_day_launch.ps1"),
    ]:
        assert path.exists()


def test_demo_day_task_map_has_fifty_tasks():
    content = Path("DEMO_DAY_10_PHASES_50_TASKS.md").read_text(encoding="utf-8")
    assert content.count("- ") >= 50
