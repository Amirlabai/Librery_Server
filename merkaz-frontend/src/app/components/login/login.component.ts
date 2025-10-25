
/**
 * LoginComponent
 * -----------------------
 * Handles user authentication.
 * Sends credentials to Flask backend and handles success/failure responses.
 * Backend is expected to respond strictly in JSON format.
 */
import { Component } from '@angular/core';
import {Router, RouterLink} from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import {CommonModule} from '@angular/common';
import {AuthService} from '../../services/auth.service';

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
  /** User input fields */
  email = '';
  password = '';

  /** UI state */
  showPassword = false;
  isLoading = false;

   /** Response messages */
  message = '';
  error = '';



  constructor(private http: HttpClient, private router: Router, private authService: AuthService ) {}

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  /**
   * Triggered on form submission.
   * Sends a POST request to Flask endpoint /login with JSON payload.
   * Backend should respond with a JSON object (see API Contract above).
   */
  onSubmit() {
    this.error = '';
    this.message = '';
    this.isLoading = true;

    const payload = {
      email: this.email.trim(),
      password: this.password.trim()
    };

    this.http.post('http://localhost:8000/login', payload, { withCredentials: true }).subscribe({
    next: (res: any) => {
    this.isLoading = false;

    if (res.token) {
      this.authService.saveToken(res.token);
    }
    if (res.role) {
      localStorage.setItem('role', res.role);
    }

    this.message = res.message || 'Login successful';
    if(res.role === 'admin'){
      this.router.navigate(['/dashboard']);
    } else {  
    this.router.navigate(['/dashboard']);
    }
  },
  error: (err) => {
    this.isLoading = false;
    this.error = err.error?.error || err.error?.message || 'Invalid credentials or server error';
  }
});

  }
}
