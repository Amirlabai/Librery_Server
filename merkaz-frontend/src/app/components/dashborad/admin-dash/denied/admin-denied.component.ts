import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

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

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadDeniedUsers();
  }

  loadDeniedUsers() {
    this.http.get<DeniedUser[]>('http://localhost:8000/admin/denied', { withCredentials: true }).subscribe({
      next: (data) => this.users = data,
      error: () => this.flashMessages = [{ type: 'error', text: 'Failed to load denied users.' }]
    });
  }

  moveToPending(email: string, index: number) {
    this.http.post(`http://localhost:8000/admin/re-pend/${email}`, {}, { withCredentials: true }).subscribe({
      next: () => {
        this.flashMessages = [{ type: 'success', text: `Moved ${email} back to pending.` }];
        this.users.splice(index, 1);
      },
      error: () => this.flashMessages = [{ type: 'error', text: `Failed to move ${email} to pending.` }]
    });
  }
}
