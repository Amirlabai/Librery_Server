import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common'; // ← חובה

interface PendingUser {
  email: string;
}

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

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadPendingUsers();
  }

  loadPendingUsers() {
    this.http
      .get<any>('http://localhost:8000/admin/pending', { withCredentials: true })
      .subscribe({
        next: (res) => {
          this.users = res.users || [];
        },
        error: (err) => {
          console.error(err);
          this.flashMessages = [{ type: 'error', text: 'Failed to load pending users.' }];
        }
      });
  }

  approveUser(email: string) {
    this.http
      .post(`http://localhost:8000/admin/approve/${email}`, {}, { withCredentials: true })
      .subscribe({
        next: () => {
          this.flashMessages = [{ type: 'success', text: `Approved ${email}` }];
          this.loadPendingUsers();
        },
        error: () => {
          this.flashMessages = [{ type: 'error', text: `Failed to approve ${email}` }];
        }
      });
  }

  denyUser(email: string) {
    this.http
      .post(`http://localhost:8000/admin/deny/${email}`, {}, { withCredentials: true })
      .subscribe({
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
