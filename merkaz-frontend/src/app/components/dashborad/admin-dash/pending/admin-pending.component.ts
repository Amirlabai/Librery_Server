import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common'; 
import { AdminDashboardService, PendingUser } from '../../../../services/admin-dashboard.service';
import { NotificationService } from '../../../../services/notifications/Notifications.service';


@Component({
  selector: 'app-admin-pending',
  standalone: true,
  imports: [RouterLink ,CommonModule],
  templateUrl: './admin-pending.component.html',
  styleUrls: ['./admin-pending.component.css']
})
export class AdminPendingComponent {
  users: PendingUser[] = [];
  
  constructor(private adminDashboardService: AdminDashboardService,private notificationService:NotificationService) {}

  ngOnInit() {
    this.loadPendingUsers();
  }

  loadPendingUsers() {

    this.adminDashboardService.loadPendingUsers().subscribe({
      next: (res) => {
      this.users = res;
      },
      error: () => {
        this.notificationService.show('Failed to load pending users.',false);
      }
    });
  }

  approveUser(email: string) {

    this.adminDashboardService.approveUser(email).subscribe({
      next: () => {
        
        this.notificationService.show(`Approved ${email}`,true);
        this.loadPendingUsers();

      },
      error: () => {
        this.notificationService.show(`Failed to approve ${email}`,false);
      }
    });
  }

  denyUser(email: string) {
    
    this.adminDashboardService.denyUser(email).subscribe({
      next: () => {
        this.notificationService.show(`Denied ${email}`,true);
        this.loadPendingUsers(); 
      },
      error: () => {
        this.notificationService.show(`Failed to deny ${email}`,false);
      }
    });
  }
}
