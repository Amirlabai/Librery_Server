import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notifications/Notifications.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ]
})
export class LoginComponent {

  email = '';
  password = '';
  showPassword = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  onSubmit() {
    this.authService.login(this.email, this.password).subscribe({
      next: (res: { token?: string; role?: string; full_name?: string }) => {
        if (!res?.token) {
          this.notificationService.show('Login failed: no token received', false);
          return;
        }
        this.authService.saveToken(res.token);
        if (res.role) {
          localStorage.setItem('role', res.role);
        }
        localStorage.setItem('email', this.email);
        if (res.full_name) {
          localStorage.setItem('fullName', res.full_name);
        }
        this.notificationService.show('Login successful', true);
        this.authService.notifyLogin();
        this.router.navigate(['/dashboard']);
      },
      error: () => {
        this.notificationService.show('Invalid credentials or server error', false);
      }
    });
  }
}
