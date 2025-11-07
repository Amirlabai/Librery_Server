import { Component, OnInit } from '@angular/core'; // Import OnInit
import { CommonModule, NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AdminDashboardService } from '../../../../services/admin-dashboard.service';

interface User {
  email: string;
  role: string;
  status: string;
  is_admin: boolean;
  is_active: boolean;
  online_status?: boolean; 
}

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, RouterLink, NgClass],
  templateUrl: './admin-user.component.html',
  styleUrls: ['./admin-user.component.css']
})
export class AdminUsersComponent implements OnInit { 
  users: User[] = [];
  flashMessages: { type: 'success' | 'error'; text: string }[] = [];
  currentUserEmail = localStorage.getItem('email') || '';


  constructor(private adminDashboardService: AdminDashboardService ) {}

  ngOnInit() {
    this.loadUsers(); 
    this.adminDashboardService.startHeartbeat();
  }

  loadUsers() {
    this.adminDashboardService.loadUsers().subscribe({
      next: (res) => {
        this.currentUserEmail = res.current_admin || localStorage.getItem('email') || '';
        this.users = res.users || [];
      },
      error: (err) => {
        console.error(err);
        this.flashMessages = [{ type: 'error', text: 'Failed to load users.' }];
      }
    });
  }

  toggleRole(email: string) {
    this.adminDashboardService.toggleRole(email).subscribe({
      next: () => {
        this.flashMessages = [{ type: 'success', text: 'Role updated successfully.' }];
        this.loadUsers();
      },
      error: () => {
        this.flashMessages = [{ type: 'error', text: 'Failed to update role.' }];
      }
    });
  }

  toggleStatus(email: string) {

    this.adminDashboardService.toggleStatus(email)
      .subscribe({
        next: () => {
          this.flashMessages = [{ type: 'success', text: 'Status updated successfully.' }];
          this.loadUsers(); 
        },
        error: () => {
          this.flashMessages = [{ type: 'error', text: 'Failed to update status.' }];
        }
      });
  }
  
}
