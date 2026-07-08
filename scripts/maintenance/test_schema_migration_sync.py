"""
Quick smoke test for check_schema_migration_sync.py
Simulates a staged addition of a new column and verifies the script detects it.
"""
import subprocess
import sys
from pathlib import Path

# scripts/maintenance/test_*.py → repo root is parents[2]
REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "backend" / "app" / "models" / "company.py"

# Backup current content
original = MODEL_PATH.read_text(encoding="utf-8")
fixture_line = '    test_field_test_hook: Mapped[str] = mapped_column(String(50), nullable=True)  # fixture\n'

# Add the fixture line, git add it
MODEL_PATH.write_text(original + fixture_line, encoding="utf-8")
r = subprocess.run(["git", "add", str(MODEL_PATH.relative_to(REPO))], cwd=REPO, capture_output=True, text=True)
print("git add:", r.returncode)

try:
    # Run the check
    r = subprocess.run(
        ["python", "scripts/maintenance/schema_migration_sync.py"],
        cwd=REPO, capture_output=True, text=True
    )
    print("\n=== STDERR ===")
    print(r.stderr[:1500])
    print("=== EXIT CODE ===")
    print(r.returncode)

    if r.returncode == 1 and "Schema migration sync violated" in r.stderr:
        print("\n[PASS] Hook correctly blocked the schema change")
        sys.exit(0)
    elif r.returncode == 0:
        print("\n[FAIL] Hook did NOT block the schema change")
        sys.exit(1)
    else:
        print(f"\n[UNEXPECTED] Hook returned {r.returncode}")
        sys.exit(2)
finally:
    # Cleanup: restore file and reset staging
    MODEL_PATH.write_text(original, encoding="utf-8")
    subprocess.run(["git", "reset", "HEAD", str(MODEL_PATH.relative_to(REPO))], cwd=REPO, capture_output=True)
    print("\n[cleanup] restored")
