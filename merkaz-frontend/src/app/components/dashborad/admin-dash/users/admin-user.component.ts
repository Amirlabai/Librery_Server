import { Component, OnInit } from '@angular/core'; // Import OnInit
import { HttpClient } from '@angular/common/http';
import { CommonModule, NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';

interface User {
  email: string;
  role: string;
  status: string;
  is_admin: boolean;
  is_active: boolean;
  online_status?: boolean; // Added optional online_status based on template
}

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, RouterLink, NgClass],
  templateUrl: './admin-user.component.html',
  styleUrls: ['./admin-user.component.css']
})
export class AdminUsersComponent implements OnInit { // Implement OnInit
  users: User[] = [];
  flashMessages: { type: 'success' | 'error'; text: string }[] = [];
  currentUserEmail = localStorage.getItem('email') || '';

  // --- Added for Pagination ---
  page: number = 1;
  totalPages: number = 1;
  // --------------------------

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadUsers(this.page); // Load the initial page
  }

  loadUsers(page: number = 1) {
    // Pass the page number as a query parameter
    this.http
      .get<any>(`http://localhost:8000/admin/users?page=${page}`, { withCredentials: true })
      .subscribe({
        next: (res) => {
          this.users = res.users || [];
          // --- Update pagination properties from response ---
          // Assuming backend returns 'page' and 'total_pages'
          this.page = res.page || 1;
          this.totalPages = res.total_pages || 1; 
          // ------------------------------------------------
        },
        error: (err) => {
          console.error(err);
          this.flashMessages = [{ type: 'error', text: 'Failed to load users.' }];
        }
      });
  }

  // --- Added for Pagination ---
  loadPage(page: number) {
    if (page > 0 && page <= this.totalPages && page !== this.page) {
      this.loadUsers(page);
    }
  }
  // --------------------------

  toggleRole(email: string) {
    this.http
      .post(`http://localhost:8000/admin/toggle-role/${email}`, {}, { withCredentials: true })
      .subscribe({
        next: () => {
          this.flashMessages = [{ type: 'success', text: 'Role updated successfully.' }];
          this.loadUsers(this.page); // Reload the *current* page
        },
        error: () => {
          this.flashMessages = [{ type: 'error', text: 'Failed to update role.' }];
        }
      });
  }

  toggleStatus(email: string) {
    this.http
      .post(`http://localhost:8000/admin/toggle-status/${email}`, {}, { withCredentials: true })
      .subscribe({
        next: () => {
          this.flashMessages = [{ type: 'success', text: 'Status updated successfully.' }];
          this.loadUsers(this.page); // Reload the *current* page
        },
        error: () => {
          this.flashMessages = [{ type: 'error', text: 'Failed to update status.' }];
        }
      });
  }
}
