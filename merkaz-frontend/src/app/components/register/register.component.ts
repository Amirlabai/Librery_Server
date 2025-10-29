import {Component} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {Router, RouterLink} from '@angular/router';
import {HttpClient} from '@angular/common/http';
import { RouterModule } from '@angular/router';


@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterModule
  ],
  styleUrls: ['./register.component.css'],
  standalone: true,
})



export class RegisterComponent{

  error = '';
  email = '';
  password = '';
  showPassword = false
  isLoading = false;
  success = '';

  private passwordPattern =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[{\]};:'",.<>/?]).{8,}$/;

  private emailPattern =
    /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  constructor(private http:HttpClient,private router:Router) {
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  onsubmit() {
    this.error = '';
    this.success = '';

    if (!this.validateForm()) return;

    const payload = {
      email: this.email.trim(),
      password: this.password.trim(),
    };

    this.isLoading = true;

    this.http.post('http://localhost:8000/register', payload).subscribe({
      next: (res: any) => {
        this.isLoading = false;

        if (res?.message) {
          this.success = res.message;

          setTimeout(() => this.router.navigate(['/login']), 2000);
        } else {
          this.success = 'Registered successfully.';
          setTimeout(() => this.router.navigate(['/login']), 2000);
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.error =
          err.error?.error ||
          err.error?.message ||
          'Registration failed. Please try again.';
      },
    });
  }
  private validateForm(): boolean {
    if (!this.email.trim() || !this.password.trim()) {
      this.error = 'Please fill in all fields.';
      return false;
    }

    if (!this.emailPattern.test(this.email)) {
      this.error = 'Please enter a valid email address.';
      return false;
    }

    if (!this.passwordPattern.test(this.password)) {
      this.error =
        'Password must contain at least 8 characters, including uppercase, lowercase, a number, and a special character.';
      return false;
    }

    return true;
  }

}
