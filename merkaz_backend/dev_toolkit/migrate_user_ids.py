"""
Migration script to add unique IDs to existing users in CSV files.

This script:
1. Scans all user CSV files (auth_users.csv, new_users.csv, denied_users.csv)
2. Assigns unique IDs to users that don't have one
3. Updates the CSV files with the new ID column format
4. Updates the ID sequence tracker file

Run this script once after implementing ID support to migrate existing data.
"""

import sys
import os
import csv

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config.config as config
from models.user_entity import User
from utils import get_next_user_id, get_max_user_id_from_files

def migrate_user_ids():
    """
    Migrates existing users to include unique IDs.
    Preserves existing IDs if present, assigns new ones if missing.
    """
    print("Starting user ID migration...")
    
    # Determine starting ID based on existing data
    max_existing_id = get_max_user_id_from_files()
    if max_existing_id > 0:
        print(f"Found existing maximum ID: {max_existing_id}")
    else:
        print("No existing IDs found. Starting from ID 1.")
    
    # Track all user files and their data
    user_files_config = [
        ("Authenticated Users", config.AUTH_USER_DATABASE),
        ("Pending Users", config.NEW_USER_DATABASE),
        ("Denied Users", config.DENIED_USER_DATABASE)
    ]
    
    total_migrated = 0
    total_with_ids = 0
    
    for label, filepath in user_files_config:
        if not os.path.exists(filepath):
            print(f"\n{label}: File not found ({filepath}), skipping...")
            continue
        
        print(f"\n{label}: Processing {filepath}...")
        
        # Read existing users
        users = User._read_users_from_file(filepath)
        
        if not users:
            print(f"  No users found in {filepath}")
            continue
        
        # Check current format and assign IDs
        users_needing_ids = []
        users_with_ids = []
        
        for user in users:
            if user.user_id is None:
                users_needing_ids.append(user)
            else:
                users_with_ids.append(user)
                total_with_ids += 1
        
        # Assign IDs to users that need them
        if users_needing_ids:
            print(f"  Found {len(users_needing_ids)} users without IDs, assigning now...")
            for user in users_needing_ids:
                user.user_id = get_next_user_id()
                total_migrated += 1
                print(f"    Assigned ID {user.user_id} to {user.email}")
        else:
            print(f"  All {len(users)} users already have IDs")
        
        # Combine all users
        all_users = users_with_ids + users_needing_ids
        
        # Save with new format (includes ID column)
        User._save_users_to_file(filepath, all_users)
        print(f"  Saved {len(all_users)} users to {filepath}")
    
    print(f"\n{'='*60}")
    print(f"Migration complete!")
    print(f"  Total users migrated (assigned new IDs): {total_migrated}")
    print(f"  Total users with existing IDs: {total_with_ids}")
    print(f"  Total users processed: {total_migrated + total_with_ids}")
    print(f"{'='*60}")
    
    # Verify the migration
    final_max_id = get_max_user_id_from_files()
    print(f"\nFinal maximum ID in system: {final_max_id}")

if __name__ == "__main__":
    try:
        migrate_user_ids()
    except Exception as e:
        print(f"\nError during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
