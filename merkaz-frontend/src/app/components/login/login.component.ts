
/**
 * LoginComponent
 * -----------------------
 * Handles user authentication.
 * Sends credentials to Flask backend and handles success/failure responses.
 * Backend is expected to respond strictly in JSON format.
 */
import { Component } from '@angular/core';
import {Router, RouterLink} from '@angular/router';
import { FormsModule } from '@angular/forms';
import {CommonModule} from '@angular/common';
import {AuthService} from '../../services/auth.service';
import { NotificationService } from '../../services/notifications/Notifications.service';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
  ]
})
export class LoginComponent {

  email = '';
  password = '';
  showPassword = false;

  constructor(private router: Router, private authService: AuthService,private notificationService:NotificationService) {}

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  /**
   * Triggered on form submission.
   * Sends a POST request to Flask endpoint /login with JSON payload.
   * Backend should respond with a JSON object (see API Contract above).
   */
  onSubmit() {

    
    this.authService.login(this.email, this.password).subscribe({

      next: (res: any) => {

        if (res.token) {
          this.authService.saveToken(res.token);
        }
        if (res.role) {
          localStorage.setItem('role', res.role);
        }
        if(res.email){
          localStorage.setItem('email',this.email);
        }

        this.notificationService.show('Login succsseful',true);

          this.router.navigate(['/dashboard']);
        },
        error: () => {
          this.notificationService.show('Invalid credentials or server error',false);
        }
    });
  }
}
