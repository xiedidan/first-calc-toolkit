#!/usr/bin/env python3
"""检查 Alembic 迁移文件链"""
import sys
import os
sys.path.insert(0, 'backend')
os.chdir('backend')

from alembic.config import Config
from alembic.script import ScriptDirectory

cfg = Config('alembic.ini')
script = ScriptDirectory.from_config(cfg)

print("=== Migration Heads ===")
heads = script.get_revisions('heads')
print(f"Found {len(heads)} head(s):")
for h in heads:
    print(f"  - {h.revision}: {h.doc}")

print("\n=== Migration Chain (last 15) ===")
count = 0
for rev in script.walk_revisions():
    down = rev.down_revision[:12] if rev.down_revision else "None"
    print(f"{rev.revision[:12]} <- {down:12} | {rev.doc}")
    count += 1
    if count >= 15:
        break

print(f"\nTotal migrations: {len(list(script.walk_revisions()))}")
