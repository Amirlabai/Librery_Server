#!/usr/bin/env python3
"""
Script to set a user as boss admin (for manual configuration by dev).
Usage: python set_boss_admin.py <email> [true|false]
"""
import sys
from models.user_entity import User

def set_boss_admin(email, is_boss_admin=True):
    """Set boss admin status for a user."""
    users = User.get_all()
    found = False
    
    for i, user in enumerate(users):
        if user.email == email:
            # Create new instance with updated boss admin status
            users[i] = User.create_user(
                email=user.email,
                password=user.password,
                role=user.role,
                status=user.status,
                user_id=user.user_id,
                is_boss_admin=is_boss_admin
            )
            User.save_all(users)
            found = True
            print(f"✓ User {email} boss admin status set to: {is_boss_admin}")
            print(f"  Role: {user.role}, Status: {user.status}, Boss Admin: {is_boss_admin}")
            break
    
    if not found:
        print(f"✗ User {email} not found in auth_users.csv")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_boss_admin.py <email> [true|false]")
        print("Example: python set_boss_admin.py admin@example.com true")
        sys.exit(1)
    
    email = sys.argv[1]
    is_boss_admin = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else True
    
    set_boss_admin(email, is_boss_admin)

