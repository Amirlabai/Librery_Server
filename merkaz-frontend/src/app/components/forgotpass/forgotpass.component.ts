import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ForgotPassService } from '../../services/forgotPass.service';

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

  constructor(private forgotPassService: ForgotPassService) {}

  onSubmit() {
    this.error = '';
    this.message = '';
    this.isLoading = true;

    this.forgotPassService.sendResetLink(this.email).subscribe({
      next: (res) => {
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
