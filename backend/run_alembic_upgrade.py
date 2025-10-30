"""运行Alembic升级"""
import subprocess
import sys

result = subprocess.run(
    ["alembic", "upgrade", "head"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

sys.exit(result.returncode)
