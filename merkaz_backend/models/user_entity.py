import csv
import config.config as config
from werkzeug.security import check_password_hash
from abc import ABC

# --- Base User Entity Class (Parent) ---
class User(ABC):
    """Base class for all user types. Implements common functionality."""
    
    def __init__(self, email, password, role='user', status='active', user_id=None):
        self.user_id = user_id  # Unique user ID
        self.email = email
        self.password = password  # This will now be a hashed password
        self.role = role
        self.status = status

    @property
    def is_admin(self):
        """Returns True if user is an admin. Overridden in Admin class."""
        return self.role == 'admin'

    @property
    def is_active(self):
        """Returns True if user status is active."""
        return self.status == 'active'

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
            "is_active": self.is_active
        }

    @staticmethod
    def create_user(email, password, role='user', status='active', user_id=None):
        """Factory method to create the appropriate user type based on role. Polymorphic factory."""
        if role == 'admin':
            return Admin(email=email, password=password, status=status, user_id=user_id)
        else:
            return RegularUser(email=email, password=password, status=status, user_id=user_id)

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
                    user_id=user.user_id
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
                
                # Determine if ID column exists (new format vs old format)
                has_id_column = header and len(header) > 0 and header[0].lower() == 'id'
                
                for row in reader:
                    if not row:
                        continue
                    
                    if has_id_column:
                        # New format: id,email,password,role,status
                        if len(row) >= 4:
                            try:
                                user_id = int(row[0]) if row[0] else None
                                email = row[1]
                                password = row[2]
                                role = row[3]
                                status = row[4] if len(row) > 4 else 'active'
                                # Use factory method for polymorphic instantiation
                                users.append(User.create_user(email=email, password=password, role=role, status=status, user_id=user_id))
                            except (ValueError, IndexError):
                                continue
                    else:
                        # Old format: email,password,role,status (backward compatibility)
                        if len(row) >= 3:
                            email = row[0]
                            password = row[1]
                            role = row[2]
                            status = row[3] if len(row) > 3 else 'active'
                            # Use factory method for polymorphic instantiation
                            users.append(User.create_user(email=email, password=password, role=role, status=status, user_id=None))
        except FileNotFoundError:
            return []
        return users

    @staticmethod
    def _save_users_to_file(filepath, users):
        """Helper to write a list of users to a given CSV file."""
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "email", "password", "role", "status"]) # Write header with ID
            for user in users:
                writer.writerow([
                    user.user_id if user.user_id is not None else '',
                    user.email,
                    user.password,
                    user.role,
                    user.status
                ])


# --- Regular User Class (Child) ---
class RegularUser(User):
    """Regular user class. Inherits from User base class."""
    
    def __init__(self, email, password, status='active', user_id=None):
        super().__init__(email, password, role='user', status=status, user_id=user_id)

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
    
    def __init__(self, email, password, status='active', user_id=None):
        super().__init__(email, password, role='admin', status=status, user_id=user_id)

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

