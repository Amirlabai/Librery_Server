import csv
import config.config as config
from werkzeug.security import check_password_hash
from abc import ABC

# --- Base User Entity Class (Parent) ---
class User(ABC):
    """Base class for all user types. Implements common functionality."""
    
    def __init__(self, email, password, role='user', status='active', user_id=None, is_boss_admin=False, first_name=None, last_name=None):
        self.user_id = user_id  # Unique user ID
        self.email = email
        self.password = password  # This will now be a hashed password
        self.role = role
        self.status = status
        self._is_boss_admin = is_boss_admin  # Boss admin status (set manually by dev)
        self.first_name = first_name
        self.last_name = last_name
        self.username = self.email.split("@")[0]
        self.__full_name = f"{first_name} {last_name}" if first_name and last_name else self.username

    @property
    def full_name(self):
        """Returns the full name of the user."""
        return self.__full_name

    @property
    def is_admin(self):
        """Returns True if user is an admin. Overridden in Admin class."""
        return self.role == 'admin'

    @property
    def is_active(self):
        """Returns True if user status is active."""
        return self.status == 'active'
    
    @property
    def is_boss_admin(self):
        """Returns True if user is a boss admin (set manually by dev)."""
        return self._is_boss_admin

    def check_password(self, password_to_check):
        """Checks the provided password against the stored hash."""
        return check_password_hash(self.password, password_to_check)

    def get_permissions(self):
        """Returns a list of permissions for this user type. Polymorphic method."""
        return []

    def can_manage_users(self):
        """Returns True if user can manage other users. Polymorphic method."""
        return False

    def to_dict(self):
        """Returns a dictionary representation of the user, safe for JSON serialization."""
        return {
            "id": self.user_id,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "is_boss_admin": self.is_boss_admin,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.__full_name,
            "username": self.username
        }

    @staticmethod
    def create_user(email, password, role='user', status='active', user_id=None, is_boss_admin=False, first_name=None, last_name=None):
        """Factory method to create the appropriate user type based on role. Polymorphic factory."""
        if role == 'admin':
            return Admin(email=email, password=password, status=status, user_id=user_id, is_boss_admin=is_boss_admin, first_name=first_name, last_name=last_name)
        else:
            return RegularUser(email=email, password=password, status=status, user_id=user_id, is_boss_admin=is_boss_admin, first_name=first_name, last_name=last_name)

    # --- Methods for Authenticated Users (auth_users.csv) ---
    @staticmethod
    def find_by_email(email):
        """Finds a user by email in the authentication database."""
        return next((user for user in User.get_all() if user.email == email), None)

    @staticmethod
    def get_all():
        """Reads all users from the authentication database."""
        return User._read_users_from_file(config.AUTH_USER_DATABASE)

    @staticmethod
    def save_all(users):
        """Rewrites the entire auth user database."""
        User._save_users_to_file(config.AUTH_USER_DATABASE, users)

    @staticmethod
    def get_admin_emails():
        """Returns a list of all admin email addresses."""
        return [user.email for user in User.get_all() if user.is_admin]

    @staticmethod
    def login_response(self):
        """Returns a login response for the user."""
        return {
            "message": "Login successful",
            "email": self.email,
            "role": "admin" if self.is_admin else "user",
            "full_name": self.full_name,
            "username": self.username,
            "token": "mock-token"
        }

    # --- Methods for Pending Users (new_users.csv) ---
    @staticmethod
    def find_pending_by_email(email):
        """Finds a user by email in the pending database."""
        return next((user for user in User.get_pending() if user.email == email), None)

    @staticmethod
    def get_pending():
        """Reads all users from the pending registration database."""
        return User._read_users_from_file(config.NEW_USER_DATABASE)

    @staticmethod
    def save_pending(users):
        """Rewrites the entire pending user database."""
        User._save_users_to_file(config.NEW_USER_DATABASE, users)

    # --- Methods for Denied Users (denied_users.csv) ---
    @staticmethod
    def find_denied_by_email(email):
        """Finds a user by email in the denied database."""
        return next((user for user in User.get_denied() if user.email == email), None)

    @staticmethod
    def get_denied():
        """Reads all users from the denied registration database."""
        return User._read_users_from_file(config.DENIED_USER_DATABASE)

    @staticmethod
    def save_denied(users):
        """Rewrites the entire denied user database."""
        User._save_users_to_file(config.DENIED_USER_DATABASE, users)

    # --- Methods for User Management ---
    @staticmethod
    def toggle_role(email):
        """Toggles the role of a user between 'admin' and 'user'. Uses polymorphism to change instance type."""
        users = User.get_all()
        for i, user in enumerate(users):
            if user.email == email:
                # Create new instance with toggled role (polymorphic behavior)
                new_role = 'user' if user.is_admin else 'admin'
                users[i] = User.create_user(
                    email=user.email,
                    password=user.password,
                    role=new_role,
                    status=user.status,
                    user_id=user.user_id,
                    is_boss_admin=user.is_boss_admin,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                User.save_all(users)
                return users[i]
        raise ValueError(f"User {email} not found")

    @staticmethod
    def toggle_status(email):
        """Toggles the status of a user between 'active' and 'inactive'."""
        users = User.get_all()
        for user in users:
            if user.email == email:
                user.status = 'inactive' if user.is_active else 'active'
                User.save_all(users)
                return user
        raise ValueError(f"User {email} not found")

    # --- Private Helper Methods ---
    @staticmethod
    def _read_users_from_file(filepath):
        """Helper to read users from a given CSV file."""
        users = []
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None) # Skip header
                
                # Determine format based on header columns
                has_id_column = header and len(header) > 0 and header[0].lower() == 'id'
                has_boss_admin_column = header and 'is_boss_admin' in [col.lower() for col in header]
                
                # Find column indices
                if has_id_column:
                    id_idx = 0
                    email_idx = 1
                    password_idx = 2
                    role_idx = 3
                    status_idx = 4
                    boss_admin_idx = 5 if has_boss_admin_column else None
                    first_name_idx = 6 if 'first_name' in [col.lower() for col in header] else None
                    last_name_idx = 7 if 'last_name' in [col.lower() for col in header] else None
                else:
                    id_idx = None
                    email_idx = 0
                    password_idx = 1
                    role_idx = 2
                    status_idx = 3
                    boss_admin_idx = 4 if has_boss_admin_column else None
                    first_name_idx = 5 if 'first_name' in [col.lower() for col in header] else None
                    last_name_idx = 6 if 'last_name' in [col.lower() for col in header] else None
                
                for row in reader:
                    if not row:
                        continue
                    
                    try:
                        user_id = int(row[id_idx]) if id_idx is not None and id_idx < len(row) and row[id_idx] else None
                        email = row[email_idx] if email_idx < len(row) else None
                        password = row[password_idx] if password_idx < len(row) else None
                        role = row[role_idx] if role_idx < len(row) else 'user'
                        status = row[status_idx] if status_idx < len(row) else 'active'
                        is_boss_admin = row[boss_admin_idx].lower() == 'true' if boss_admin_idx is not None and boss_admin_idx < len(row) and row[boss_admin_idx] else False
                        first_name = row[first_name_idx] if first_name_idx is not None and first_name_idx < len(row) else None
                        last_name = row[last_name_idx] if last_name_idx is not None and last_name_idx < len(row) else None
                        if not email or not password:
                            continue
                            
                        # Use factory method for polymorphic instantiation
                        users.append(User.create_user(
                            email=email, 
                            password=password, 
                            role=role, 
                            status=status, 
                            user_id=user_id,
                            is_boss_admin=is_boss_admin,
                            first_name=first_name,
                            last_name=last_name
                        ))
                    except (ValueError, IndexError):
                        continue
        except FileNotFoundError:
            return []
        return users

    @staticmethod
    def _save_users_to_file(filepath, users):
        """Helper to write a list of users to a given CSV file."""
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header with all columns including is_boss_admin
            writer.writerow(["id", "email", "password", "role", "status", "is_boss_admin", "first_name", "last_name"])
            for user in users:
                writer.writerow([
                    user.user_id if user.user_id is not None else '',
                    user.email,
                    user.password,
                    user.role,
                    user.status,
                    'true' if user.is_boss_admin else 'false',
                    user.first_name if user.first_name is not None else '',
                    user.last_name if user.last_name is not None else ''
                ])


# --- Regular User Class (Child) ---
class RegularUser(User):
    """Regular user class. Inherits from User base class."""
    
    def __init__(self, email, password, status='active', user_id=None, is_boss_admin=False, first_name=None, last_name=None):
        super().__init__(email, password, role='user', status=status, user_id=user_id, is_boss_admin=is_boss_admin, first_name=first_name, last_name=last_name)

    @property
    def is_admin(self):
        """Regular users are not admins."""
        return False

    def get_permissions(self):
        """Returns permissions for regular users."""
        return ['view_files', 'download_files', 'upload_files']

    def can_manage_users(self):
        """Regular users cannot manage other users."""
        return False


# --- Admin User Class (Child) ---
class Admin(User):
    """Admin user class. Inherits from User base class with admin privileges."""
    
    def __init__(self, email, password, status='active', user_id=None, is_boss_admin=False, first_name=None, last_name=None):
        super().__init__(email, password, role='admin', status=status, user_id=user_id, is_boss_admin=is_boss_admin, first_name=first_name, last_name=last_name)

    @property
    def is_admin(self):
        """Admin users are always admins."""
        return True

    def get_permissions(self):
        """Returns permissions for admin users. Overrides parent method."""
        return [
            'view_files', 
            'download_files', 
            'upload_files',
            'manage_users',
            'approve_users',
            'deny_users',
            'view_metrics',
            'view_logs',
            'toggle_user_roles',
            'toggle_user_status'
        ]

    def can_manage_users(self):
        """Admin users can manage other users. Overrides parent method."""
        return True

