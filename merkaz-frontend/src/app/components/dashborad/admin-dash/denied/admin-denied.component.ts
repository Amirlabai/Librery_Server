import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AdminDashboardService } from '../../../../services/admin-dashboard.service';
import { NotificationService } from '../../../../services/notifications/Notifications.service';

interface DeniedUser {
  email: string;
}

@Component({
  selector: 'app-admin-denied',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './admin-denied.component.html',
  styleUrls: ['./admin-denied.component.css']
})

export class AdminDeniedComponent {

  users: DeniedUser[] = [];

  constructor(private adminDashboardService: AdminDashboardService,private notificationsService:NotificationService) {}

  ngOnInit() {
    this.loadDeniedUsers();
  }

  loadDeniedUsers() {
    this.adminDashboardService.loadDeniedUsers().subscribe({
      next: (data) => {
        this.users = data;
      },
      error: () => {
        this.notificationsService.show('Failed to load denied users.',false)
      }
    });
  }

  moveToPending(email: string, index: number) {
    this.adminDashboardService.moveToPending(email).subscribe({
      next: () => {

        this.notificationsService.show(`Moved ${email} back to pending.`,true)
        this.users.splice(index, 1); 
      
      },
      error: () => {
        this.notificationsService.show(`Failed to move ${email} to pending.`,false)
      }
    });
  }
}
