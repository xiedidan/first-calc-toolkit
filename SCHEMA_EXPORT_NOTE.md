# Schema Export Note

## Current Export Strategy

The build script exports **ONLY the `public` schema**:

```powershell
pg_dump -n public -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
```

## What Gets Exported

### Included
- All tables in `public` schema
- All views in `public` schema
- All functions/procedures in `public` schema
- All sequences in `public` schema

### Excluded
- `his_view` schema (and any other schemas)
- System catalogs
- Template databases

## About the `his_view.TMP` Error

If you see an error like:
```
ERROR: value too long for type character(1)
INSERT INTO "his_view"."TMP" ...
```

This means:
1. **The error is NOT from our export** (we don't export `his_view` schema)
2. The error is from a previous/different database dump
3. Or there's a table with the same name in `public` schema

## Verification

To verify what schemas are in the export:

```bash
# Check schemas in SQL file
grep "CREATE SCHEMA" database.sql

# Should only see:
# CREATE SCHEMA public;
```

## If You Need to Export Multiple Schemas

Modify the export command:

```powershell
# Export multiple schemas
pg_dump -n public -n his_view ...

# Or export all schemas (not recommended)
pg_dump ...  # (without -n flag)
```

## Recommended: Clean Database Before Import

Before importing, ensure the target database is clean:

```sql
-- Drop and recreate public schema
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

This is already handled by `init-database.sh` when you choose option 1.

## Troubleshooting

### Issue: Tables from other schemas appear in export

**Check**: Verify the export command includes `-n public`

### Issue: Import fails with schema errors

**Solution**: 
1. Clean the database first (option 1 in init-database.sh)
2. Or manually drop conflicting schemas before import

### Issue: Data type mismatch errors

**Cause**: The source and target databases have different table definitions

**Solution**:
1. Ensure both databases use the same schema version
2. Run Alembic migrations on target database first
3. Or use a clean database and let the SQL dump create all tables
