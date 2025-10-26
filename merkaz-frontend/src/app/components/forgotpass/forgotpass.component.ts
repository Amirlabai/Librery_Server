import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './forgotpass.component.html',
  styleUrls: ['./forgotpass.component.css']
})
export class ForgotPasswordComponent {
  email = '';
  isLoading = false;
  message = '';
  error = '';

  constructor(private http: HttpClient) {}

  onSubmit() {
    this.error = '';
    this.message = '';
    this.isLoading = true;

    const payload = { email: this.email.trim() };

    this.http.post('http://localhost:8000/forgot-password', payload).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.message = res.message || 'Password reset link sent to your email.';
      },
      error: (err) => {
        this.isLoading = false;
        this.error =
          err.error?.error ||
          err.error?.message ||
          'Failed to send reset link. Please try again later.';
      }
    });
  }
}
