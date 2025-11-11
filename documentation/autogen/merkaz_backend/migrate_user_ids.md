# Module `merkaz_backend/migrate_user_ids.py`

Migration script to add unique IDs to existing users in CSV files.

This script:
1. Scans all user CSV files (auth_users.csv, new_users.csv, denied_users.csv)
2. Assigns unique IDs to users that don't have one
3. Updates the CSV files with the new ID column format
4. Updates the ID sequence tracker file

Run this script once after implementing ID support to migrate existing data.

## Functions

### `migrate_user_ids()`

Migrates existing users to include unique IDs.
Preserves existing IDs if present, assigns new ones if missing.
