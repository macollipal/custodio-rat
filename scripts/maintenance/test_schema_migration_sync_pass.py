"""
Test 2: verifies the hook PASSES when a migration is included.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "backend" / "app" / "models" / "company.py"
MIGRATION_PATH = REPO / "backend" / "migrations" / "_test_fixture_migration.sql"

original_model = MODEL_PATH.read_text(encoding="utf-8")
fixture_line = '    test_field_test_hook_pass: Mapped[str] = mapped_column(String(50), nullable=True)  # fixture\n'
fixture_model_with_migration = '    test_field_test_hook_pass: Mapped[str] = mapped_column(String(50), nullable=True)  # fixture with migration\n'

# Setup: modify model + migration
MODEL_PATH.write_text(original_model + fixture_model_with_migration, encoding="utf-8")
MIGRATION_PATH.write_text("-- Test fixture migration\nALTER TABLE companies ADD COLUMN test_field_test_hook_pass VARCHAR(50);\n", encoding="utf-8")

try:
    rel_model = str(MODEL_PATH.relative_to(REPO))
    rel_migration = str(MIGRATION_PATH.relative_to(REPO))

    subprocess.run(["git", "add", rel_model], cwd=REPO, capture_output=True)
    subprocess.run(["git", "add", rel_migration], cwd=REPO, capture_output=True)

    r = subprocess.run(
        ["python", "scripts/maintenance/schema_migration_sync.py"],
        cwd=REPO, capture_output=True, text=True
    )

    if r.returncode == 0:
        print("[PASS] Hook correctly allowed when migration is included")
        sys.exit(0)
    else:
        print("[FAIL] Hook incorrectly blocked when migration was included")
        print("STDERR:", r.stderr)
        sys.exit(1)
finally:
    MODEL_PATH.write_text(original_model, encoding="utf-8")
    subprocess.run(["git", "reset", "HEAD", rel_model], cwd=REPO, capture_output=True)
    if MIGRATION_PATH.exists():
        MIGRATION_PATH.unlink()
    print("[cleanup] restored")
