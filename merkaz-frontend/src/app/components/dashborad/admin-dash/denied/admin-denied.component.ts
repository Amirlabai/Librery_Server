import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AdminDashboardService } from '../../../../services/admin-dashboard.service';

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
  flashMessages: { type: 'success' | 'error'; text: string }[] = [];

  constructor(private adminDashboardService: AdminDashboardService) {}

  ngOnInit() {
    this.loadDeniedUsers();
  }

  loadDeniedUsers() {
    this.adminDashboardService.loadDeniedUsers().subscribe({
      next: (data) => {
        this.users = data;
      },
      error: () => {
        this.flashMessages = [{ type: 'error', text: 'Failed to load denied users.' }];
      }
    });
  }

  moveToPending(email: string, index: number) {
  this.adminDashboardService.moveToPending(email).subscribe({
    next: () => {
      this.flashMessages = [{ type: 'success', text: `Moved ${email} back to pending.` }];
      this.users.splice(index, 1); 
    },
    error: () => {
      this.flashMessages = [{ type: 'error', text: `Failed to move ${email} to pending.` }];
    }
  });
}
}
