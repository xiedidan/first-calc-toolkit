# Circular Foreign Key - Not a Problem

## The Warning

When exporting with `pg_dump --data-only`, you may see:

```
pg_dump: warning: there are circular foreign-key constraints on this table:
pg_dump: detail: model_nodes
pg_dump: hint: You might not be able to restore the dump without using --disable-triggers
```

## Root Cause

The `model_nodes` table has a **self-referencing foreign key** for tree structure:

```python
parent_id = Column(Integer, ForeignKey("model_nodes.id", ondelete="CASCADE"))
```

## Why This Warning Appears

The warning only appears when using `--data-only` export because:
- Data-only exports don't include CREATE TABLE statements
- Without table definitions, pg_dump can't determine the correct insertion order
- It warns about potential issues during restore

## Why We Don't Need --disable-triggers

**We're NOT using `--data-only`!**

Our export command:
```bash
pg_dump -n public --no-owner --no-acl
```

This exports:
1. **Schema first** (CREATE TABLE statements)
2. **Then data** (INSERT statements)

When exporting both schema and data together:
- `pg_dump` automatically handles the correct order
- Foreign key constraints are created AFTER all data is inserted
- No circular dependency issues

## How pg_dump Handles This

The generated SQL looks like:

```sql
-- 1. Create tables (without constraints)
CREATE TABLE model_nodes (...);

-- 2. Insert all data (no constraints yet)
INSERT INTO model_nodes VALUES (...);
INSERT INTO model_nodes VALUES (...);

-- 3. Add foreign key constraints (after all data is in)
ALTER TABLE model_nodes ADD CONSTRAINT fk_parent 
  FOREIGN KEY (parent_id) REFERENCES model_nodes(id);
```

This order ensures:
- All nodes are inserted first
- Constraints are added last
- No circular dependency issues

## Our Solution

Export schema and data together (not data-only):

```bash
pg_dump -n public --no-owner --no-acl
```

This automatically:
- Creates tables first
- Inserts data second
- Adds constraints last
- Handles circular dependencies correctly

## When Would You Need --disable-triggers?

Only if you're doing `--data-only` export:

```bash
# This would need --disable-triggers
pg_dump --data-only ...

# Our approach doesn't need it
pg_dump -n public ...
```

## Other Tables with Self-Referencing Foreign Keys

Check if other tables have similar patterns:

```sql
SELECT 
    conrelid::regclass AS table_name,
    conname AS constraint_name
FROM pg_constraint
WHERE contype = 'f' 
  AND conrelid = confrelid;
```

Currently, only `model_nodes` has this pattern in our database.

## Verification

After restore, verify the foreign key constraints:

```sql
-- Check for orphaned records
SELECT id, parent_id, name 
FROM model_nodes 
WHERE parent_id IS NOT NULL 
  AND parent_id NOT IN (SELECT id FROM model_nodes);
```

Should return 0 rows if all constraints are satisfied.

## Related Files

- `scripts/build-offline-package.ps1` - PowerShell script (fixed)
- `scripts/build-offline-package.sh` - Bash script (fixed)
- `backend/app/models/model_node.py` - Model definition
