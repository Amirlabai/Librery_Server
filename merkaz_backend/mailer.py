from flask_mail import Mail, Message
from flask import url_for, current_app
import config
from user import User
import threading

mail = Mail()

def _send_new_user_notification_sync(app, user_email, pending_url):
    """Internal function that actually sends the email (runs in background thread)."""
    with app.app_context():
        admin_emails = User.get_admin_emails()
        if not admin_emails:
            current_app.logger.warning("No admin users found to send new user notification.")
            return

        msg = Message(
            'New User Registration',
            sender=config.MAIL_DEFAULT_SENDER,
            recipients=admin_emails
        )
        msg.html = f"""
        <p>Hello Admin,</p>
        <p>A new user with the email <b>{user_email}</b> has registered and is awaiting approval.</p>
        <p>Please review the request on the <a href="{pending_url}">Pending Approvals</a> page.</p>
        <p>Thank you!</p>
        """
        try:
            mail.send(msg)
            current_app.logger.info(f"Admin notification sent for {user_email} to: {', '.join(admin_emails)}")
        except Exception as e:
            current_app.logger.error(f"Error sending admin notification: {e}")

def send_new_user_notification(app, user_email):
    """Notifies all admins that a new user has registered (asynchronously)."""
    # Generate URL in the request context before starting the thread
    pending_url = url_for('admin.admin_pending', _external=True)
    pending_url = "http://localhost:4200/pending"
    thread = threading.Thread(target=_send_new_user_notification_sync, args=(app, user_email, pending_url))
    thread.daemon = True
    thread.start()

def _send_approval_email_sync(app, user_email, login_url):
    """Internal function that actually sends the email (runs in background thread)."""
    with app.app_context():
        msg = Message(
            'Your Account has been Approved!',
            sender=config.MAIL_DEFAULT_SENDER,
            recipients=[user_email]
        )
        msg.html = f"""
        <p>Hello,</p>
        <p>Congratulations! Your account for Merkaz_lib has been approved by an administrator.</p>
        <p>You can now log in to access the file library.</p>
        <p><a href="{login_url}">Click here to Login</a></p>
        <p>Thank you!</p>
        """
        try:
            mail.send(msg)
            current_app.logger.info(f"Approval email sent to {user_email}")
        except Exception as e:
            current_app.logger.error(f"Error sending approval email: {e}")

def send_approval_email(app, user_email):
    """Sends an email to the user when their account is approved (asynchronously)."""
    # Generate URL in the request context before starting the thread
    login_url = url_for('auth.api_login', _external=True)
    thread = threading.Thread(target=_send_approval_email_sync, args=(app, user_email, login_url))
    thread.daemon = True
    thread.start()

def _send_denial_email_sync(app, user_email):
    """Internal function that actually sends the email (runs in background thread)."""
    with app.app_context():
        msg = Message(
            'Your Registration Status',
            sender=config.MAIL_DEFAULT_SENDER,
            recipients=[user_email]
        )
        msg.html = """
        <p>Hello,</p>
        <p>We regret to inform you that your registration for Merkaz_lib has been denied at this time.</p>
        <p>If you believe this was a mistake, please contact an administrator.</p>
        <p>Thank you.</p>
        """
        try:
            mail.send(msg)
            current_app.logger.info(f"Denial email sent to {user_email}")
        except Exception as e:
            current_app.logger.error(f"Error sending denial email: {e}")

def send_denial_email(app, user_email):
    """Sends an email to the user when their account is denied (asynchronously)."""
    thread = threading.Thread(target=_send_denial_email_sync, args=(app, user_email))
    thread.daemon = True
    thread.start()

def _send_password_reset_email_sync(app, user_email, token, reset_url):
    """Internal function that actually sends the email (runs in background thread)."""
    with app.app_context():
        msg = Message(
            'Password Reset Request',
            sender=config.MAIL_DEFAULT_SENDER,
            recipients=[user_email]
        )
        msg.html = f"""
        <p>Hello,</p>
        <p>You requested a password reset. Click the link below to set a new password. This link will expire in one hour.</p>
        <p><a href="{reset_url}">Reset Your Password</a></p>
        <p>If you did not request this, please ignore this email.</p>
        """
        try:
            mail.send(msg)
            current_app.logger.info(f"Password reset email sent to {user_email}")
        except Exception as e:
            current_app.logger.error(f"Error sending password reset email: {e}")

def send_password_reset_email(app, user_email, token):
    """Sends a password reset email to the user (asynchronously)."""
    # Generate URL in the request context before starting the thread
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    thread = threading.Thread(target=_send_password_reset_email_sync, args=(app, user_email, token, reset_url))
    thread.daemon = True
    thread.start()