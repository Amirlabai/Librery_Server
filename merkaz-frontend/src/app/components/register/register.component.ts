import {Component} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {Router, RouterLink} from '@angular/router';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notifications/Notifications.service';


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

  email = '';
  password = '';
  showPassword = false
  first_name = '';
  last_name = '';
  
  private passwordPattern =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[{\]};:'",.<>/?]).{8,}$/;

  private emailPattern =
    /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  constructor(private router: Router, private authService: AuthService,private notificationsService:NotificationService) {}

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  onsubmit() {

    if (!this.validateForm()) return;

    this.first_name.toLowerCase();
    this.last_name.toLocaleLowerCase();

    

    this.authService.register(this.first_name,this.last_name,this.email, this.password).subscribe({

      next: () => {
        
        this.notificationsService.show('Registered Succssefully',true)  
        setTimeout(() => this.router.navigate(['/login']), 2000);
        
      },
      error: () => {
        this.notificationsService.show('Registration failed. Please try again.',false);
      },
    });
  }
  private validateForm(): boolean {
    
    if (!this.email.trim() || !this.password.trim()) {

      this.notificationsService.show('Please fill in all fields.',false)
      return false;
    }

    if (!this.emailPattern.test(this.email)) {

      this.notificationsService.show('Please enter a valid email address.',false)
      return false;
    }

    if (!this.passwordPattern.test(this.password)) {

      this.notificationsService.show('Password must contain at least 8 characters, including uppercase, lowercase, a number, and a special character.',false);
      return false;
    }

    return true;
  }

}
