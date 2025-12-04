#!/usr/bin/env python3
"""
Tkinter GUI for managing boss admin status.
Shows a list of users and allows setting/revoking boss admin status.
Usage: python set_boss_admin_gui.py
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add parent directory (merkaz_backend) to path to import modules
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _backend_dir)

from models.user_entity import User
from config.config import ICON_PATH

class BossAdminGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Boss Admin Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set window icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), ICON_PATH)
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            # Icon loading failed, but continue without it
            pass
        
        # Load users
        self.users = User.get_all()
        self.selected_user = None
        
        self.create_widgets()
        self.refresh_user_list()
    
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Boss Admin Management", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Left panel - User list
        left_frame = ttk.LabelFrame(main_frame, text="All Users", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # Search box
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # User listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.user_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       selectmode=tk.SINGLE, font=("Arial", 10))
        self.user_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.user_listbox.bind('<<ListboxSelect>>', self.on_user_select)
        
        scrollbar.config(command=self.user_listbox.yview)
        
        # Right panel - User details and actions
        right_frame = ttk.LabelFrame(main_frame, text="User Details & Actions", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        
        # User info display
        info_frame = ttk.Frame(right_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        info_frame.columnconfigure(1, weight=1)
        
        self.info_labels = {}
        fields = [
            ("Email:", "email"),
            ("Role:", "role"),
            ("Status:", "status"),
            ("User ID:", "user_id"),
            ("Boss Admin:", "is_boss_admin")
        ]
        
        for i, (label_text, field) in enumerate(fields):
            ttk.Label(info_frame, text=label_text, font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            value_label = ttk.Label(info_frame, text="", font=("Arial", 10))
            value_label.grid(row=i, column=1, sticky=tk.W, pady=5)
            self.info_labels[field] = value_label
        
        # Boss admin status indicator
        self.boss_admin_indicator = ttk.Label(
            right_frame, text="", font=("Arial", 12, "bold"), foreground="green"
        )
        self.boss_admin_indicator.grid(row=1, column=0, pady=(0, 20))
        
        # Action buttons frame
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Set as Boss Admin button
        self.set_boss_btn = ttk.Button(
            button_frame, text="Set as Boss Admin", 
            command=self.set_boss_admin, state=tk.DISABLED
        )
        self.set_boss_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        
        # Revoke Boss Admin button
        self.revoke_boss_btn = ttk.Button(
            button_frame, text="Revoke Boss Admin", 
            command=self.revoke_boss_admin, state=tk.DISABLED
        )
        self.revoke_boss_btn.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
        
        # Boss Admins list frame
        boss_admins_frame = ttk.LabelFrame(right_frame, text="Current Boss Admins", padding="10")
        boss_admins_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        boss_admins_frame.columnconfigure(0, weight=1)
        boss_admins_frame.rowconfigure(0, weight=1)
        
        boss_scrollbar = ttk.Scrollbar(boss_admins_frame)
        boss_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.boss_admins_listbox = tk.Listbox(
            boss_admins_frame, yscrollcommand=boss_scrollbar.set,
            font=("Arial", 9), height=5
        )
        self.boss_admins_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.boss_admins_listbox.bind('<<ListboxSelect>>', self.on_boss_admin_select)
        
        boss_scrollbar.config(command=self.boss_admins_listbox.yview)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(right_frame)
        bottom_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.columnconfigure(2, weight=1)
        
        ttk.Button(bottom_frame, text="Refresh", command=self.refresh_user_list).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        ttk.Button(bottom_frame, text="OK", command=self.on_ok).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(bottom_frame, text="Cancel", command=self.on_cancel).grid(
            row=0, column=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
    
    def get_username(self, email):
        """Extract username part from email (before @)."""
        return email.split('@')[0] if '@' in email else email
    
    def refresh_user_list(self):
        """Refresh the user list and boss admins list."""
        # Reload users from database
        self.users = User.get_all()
        
        # Clear and populate user listbox
        self.user_listbox.delete(0, tk.END)
        self.filtered_users = []
        
        search_term = self.search_var.get().lower()
        for user in self.users:
            username = self.get_username(user.email)
            display_text = f"{username} ({user.role})"
            # Search in both username and full email for better search experience
            if not search_term or search_term in display_text.lower() or search_term in user.email.lower():
                self.user_listbox.insert(tk.END, display_text)
                self.filtered_users.append(user)
        
        # Update boss admins list
        self.update_boss_admins_list()
        
        # Clear selection
        self.user_listbox.selection_clear(0, tk.END)
        self.selected_user = None
        self.update_user_info()
    
    def on_search_change(self, *args):
        """Handle search box changes."""
        self.refresh_user_list()
    
    def update_boss_admins_list(self):
        """Update the boss admins listbox."""
        self.boss_admins_listbox.delete(0, tk.END)
        boss_admins = [user for user in self.users if user.is_boss_admin]
        
        for user in boss_admins:
            username = self.get_username(user.email)
            display_text = f"{username} ({user.role})"
            self.boss_admins_listbox.insert(tk.END, display_text)
    
    def on_user_select(self, event):
        """Handle user selection from main list."""
        selection = self.user_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_user = self.filtered_users[index]
            self.update_user_info()
    
    def on_boss_admin_select(self, event):
        """Handle boss admin selection from boss admins list."""
        selection = self.boss_admins_listbox.curselection()
        if selection:
            # Get the username from the display text
            display_text = self.boss_admins_listbox.get(selection[0])
            username = display_text.split(' (')[0]
            role = display_text.split(' (')[1].rstrip(')')
            
            # Find matching user by username and role (since username might not be unique)
            for i, user in enumerate(self.filtered_users):
                if self.get_username(user.email) == username and user.role == role:
                    self.user_listbox.selection_clear(0, tk.END)
                    self.user_listbox.selection_set(i)
                    self.user_listbox.see(i)
                    self.selected_user = user
                    self.update_user_info()
                    break
    
    def update_user_info(self):
        """Update the user info display and button states."""
        if self.selected_user:
            user = self.selected_user
            self.info_labels["email"].config(text=user.email)
            self.info_labels["role"].config(text=user.role)
            self.info_labels["status"].config(text=user.status)
            self.info_labels["user_id"].config(text=str(user.user_id) if user.user_id else "N/A")
            
            boss_status = "Yes" if user.is_boss_admin else "No"
            self.info_labels["is_boss_admin"].config(text=boss_status)
            
            # Update indicator
            if user.is_boss_admin:
                self.boss_admin_indicator.config(
                    text="✓ BOSS ADMIN", foreground="green"
                )
            else:
                self.boss_admin_indicator.config(text="", foreground="green")
            
            # Update button states
            if user.is_boss_admin:
                self.set_boss_btn.config(state=tk.DISABLED)
                self.revoke_boss_btn.config(state=tk.NORMAL)
            else:
                self.set_boss_btn.config(state=tk.NORMAL)
                self.revoke_boss_btn.config(state=tk.DISABLED)
        else:
            # Clear info display
            for label in self.info_labels.values():
                label.config(text="")
            self.boss_admin_indicator.config(text="")
            self.set_boss_btn.config(state=tk.DISABLED)
            self.revoke_boss_btn.config(state=tk.DISABLED)
    
    def set_boss_admin(self):
        """Set selected user as boss admin."""
        if not self.selected_user:
            return
        
        user = self.selected_user
        if user.is_boss_admin:
            messagebox.showinfo("Info", f"{user.email} is already a boss admin.")
            return
        
        # Confirm action
        if messagebox.askyesno(
            "Confirm", 
            f"Set {user.email} as boss admin?\n\nRole: {user.role}\nStatus: {user.status}"
        ):
            try:
                users = User.get_all()
                for i, u in enumerate(users):
                    if u.email == user.email:
                        users[i] = User.create_user(
                            email=u.email,
                            password=u.password,
                            role=u.role,
                            status=u.status,
                            user_id=u.user_id,
                            is_boss_admin=True
                        )
                        User.save_all(users)
                        break
                
                messagebox.showinfo("Success", f"{user.email} is now a boss admin.")
                self.refresh_user_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set boss admin:\n{str(e)}")
    
    def revoke_boss_admin(self):
        """Revoke boss admin status from selected user."""
        if not self.selected_user:
            return
        
        user = self.selected_user
        if not user.is_boss_admin:
            messagebox.showinfo("Info", f"{user.email} is not a boss admin.")
            return
        
        # Confirm action
        if messagebox.askyesno(
            "Confirm", 
            f"Revoke boss admin status from {user.email}?\n\nRole: {user.role}\nStatus: {user.status}"
        ):
            try:
                users = User.get_all()
                for i, u in enumerate(users):
                    if u.email == user.email:
                        users[i] = User.create_user(
                            email=u.email,
                            password=u.password,
                            role=u.role,
                            status=u.status,
                            user_id=u.user_id,
                            is_boss_admin=False
                        )
                        User.save_all(users)
                        break
                
                messagebox.showinfo("Success", f"Boss admin status revoked from {user.email}.")
                self.refresh_user_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to revoke boss admin:\n{str(e)}")
    
    def on_ok(self):
        """Handle OK button click."""
        messagebox.showinfo("Info", "Changes saved. Closing application.")
        self.root.destroy()
    
    def on_cancel(self):
        """Handle Cancel button click."""
        if messagebox.askyesno("Confirm", "Close without saving changes?"):
            self.root.destroy()

def main():
    """Main entry point."""
    try:
        root = tk.Tk()
        app = BossAdminGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

