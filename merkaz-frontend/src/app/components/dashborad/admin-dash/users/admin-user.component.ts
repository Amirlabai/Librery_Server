import { Component, OnInit } from '@angular/core'; // Import OnInit
import { CommonModule, NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AdminDashboardService } from '../../../../services/admin-dashboard.service';
import { NotificationService } from '../../../../services/notifications/Notifications.service';

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


  constructor(private adminDashboardService: AdminDashboardService,private notificationService:NotificationService ) {}

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
      error: () => {
        this.notificationService.show('Failed to load users.',false);
      }
    });
  }

  toggleRole(email: string) {
    this.adminDashboardService.toggleRole(email).subscribe({
      next: () => {
        this.notificationService.show('Role updated successfully.',true);
        this.loadUsers();
      },
      error: () => {
        this.notificationService.show('Failed to update role.',false);
      }
    });
  }

  toggleStatus(email: string) {

    this.adminDashboardService.toggleStatus(email)
      .subscribe({

        next: () => {
          this.notificationService.show('Status updated successfully.',true);
          this.loadUsers(); 

        },
        error: () => {
          this.notificationService.show('Failed to update status.',false);
        }
      
      });
  }
  
}
