# Offline Package Script - Simplified Version

## Changes Made

### Simplified Strategy

**Before**: Selective export with exclude list
- Maintained `.offline-package-exclude-tables.txt`
- Complex logic to exclude specific tables
- Multiple steps: schema + data + merge

**After**: Full public schema export
- Export entire `public` schema
- Single `pg_dump` command
- Much simpler and faster

## Key Changes

### 1. Removed Exclude List Logic

No longer need:
- `.offline-package-exclude-tables.txt` file
- Complex file reading and filtering
- Separate schema and data exports

### 2. Simplified pg_dump Command

```powershell
# New simplified command
pg_dump -n public --no-owner --no-acl
```

Parameters:
- `-n public` - Export only public schema
- `--no-owner` - Don't include ownership commands
- `--no-acl` - Don't include access control commands

Note: No need for `--disable-triggers` because we're exporting schema+data together, not data-only

### 3. Single Export Step

Before (3 steps):
1. Export schema only
2. Export data with exclusions
3. Merge files

After (1 step):
1. Export public schema (structure + data)

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| Complexity | High | Low |
| Maintenance | Need to update exclude list | No maintenance |
| Speed | Slower (3 operations) | Faster (1 operation) |
| File size | Smaller (excluded data) | Larger (all data) |
| Reliability | More points of failure | Single operation |

## What Gets Exported

### Included
- All tables in `public` schema
- All table data
- All indexes
- All constraints
- All sequences
- All functions/procedures in public schema

### Excluded
- Other schemas (if any)
- System catalogs
- Ownership information
- Access control lists

## File Size Comparison

Typical sizes:
- **Development database**: 50-200 MB compressed
- **Production database**: 200-1000 MB compressed

The full schema export (not data-only) ensures:
- Self-referencing foreign keys work correctly
- Constraints are added after data insertion
- No constraint violations during restore

## Usage

```powershell
# Run the simplified script
.\scripts\build-offline-package.ps1

# Or start from specific step
.\scripts\build-offline-package.ps1 -StartFrom 4
```

## Script Structure

```
Step 1/5: Pull base images
Step 2/5: Build Docker images  
Step 3/5: Export Docker images
Step 4/5: Export database (public schema)
Step 5/5: Create final package
```

## Restore Process

The exported SQL will include:

```sql
-- 1. Create tables (without constraints)
CREATE TABLE model_nodes (...);

-- 2. Insert all data
INSERT INTO model_nodes VALUES (...);
INSERT INTO model_nodes VALUES (...);

-- 3. Add constraints (after data is in)
ALTER TABLE model_nodes ADD CONSTRAINT fk_parent 
  FOREIGN KEY (parent_id) REFERENCES model_nodes(id);
```

This order ensures no circular dependency issues.

## Troubleshooting

### Issue: pg_dump shows circular foreign key warning

**Solution**: This is just a warning, not an error. The export will complete successfully because we're exporting schema+data together (not data-only)

### Issue: File too large

**Options**:
1. Use higher compression: `-mx=9` (already used)
2. Clean up old data before export
3. Use incremental backups

### Issue: Restore fails with constraint violations

**Check**:
1. Ensure you're restoring to an empty database
2. Verify SQL file contains both CREATE and INSERT statements
3. Check that constraints are added AFTER data insertion

## Related Files

- `scripts/build-offline-package.ps1` - Main script (simplified)
- `scripts/build-offline-package.sh` - Bash version (to be updated)
- `CIRCULAR_FOREIGN_KEY_FIX.md` - Explanation of --disable-triggers
- `backend/.env` - Database connection config

## Migration from Old Version

If you have the old version with exclude list:

1. The new script doesn't use `.offline-package-exclude-tables.txt`
2. All data will be exported (larger file size)
3. No need to maintain exclude list anymore
4. Simpler and more reliable

## Performance

Typical export times:
- Small database (< 100 MB): 1-2 minutes
- Medium database (100-500 MB): 3-5 minutes  
- Large database (> 500 MB): 5-15 minutes

Compression adds ~30% to export time but reduces file size by 70-90%.
