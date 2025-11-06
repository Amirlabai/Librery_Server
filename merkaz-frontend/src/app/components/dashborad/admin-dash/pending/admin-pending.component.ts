import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common'; 
import { AdminDashboardService, PendingUser } from '../../../../services/admin-dashboard.service';


@Component({
  selector: 'app-admin-pending',
  standalone: true,
  imports: [RouterLink ,CommonModule],
  templateUrl: './admin-pending.component.html',
  styleUrls: ['./admin-pending.component.css']
})
export class AdminPendingComponent {
  users: PendingUser[] = [];
  flashMessages: { type: string; text: string }[] = [];

  constructor(private http: HttpClient,private adminDashboardService: AdminDashboardService) {}

  ngOnInit() {
    this.loadPendingUsers();
  }

  loadPendingUsers() {

    this.adminDashboardService.loadPendingUsers().subscribe({
      next: (res) => {
      this.users = res;
      },
      error: (err) => {
        this.flashMessages = [{ type: 'error', text: 'Failed to load pending users.' }];
      }
    });
  }

  approveUser(email: string) {

    this.adminDashboardService.approveUser(email).subscribe({
      next: () => {
        this.flashMessages = [{ type: 'success', text: `Approved ${email}` }];
        this.loadPendingUsers();
        setTimeout(() => this.flashMessages = [], 3000);
      },
      error: () => {
        this.flashMessages = [{ type: 'error', text: `Failed to approve ${email}` }];
      }
    });
  }

  denyUser(email: string) {
    
    this.adminDashboardService.denyUser(email).subscribe({
      next: () => {
        this.flashMessages = [{ type: 'success', text: `Denied ${email}` }];
        this.loadPendingUsers(); 
      },
      error: () => {
        this.flashMessages = [{ type: 'error', text: `Failed to deny ${email}` }];
      }
    });
  }
}
