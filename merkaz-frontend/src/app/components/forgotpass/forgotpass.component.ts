import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ForgotPassService } from '../../services/forgotPass.service';
import { NotificationService } from '../../services/notifications/Notifications.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './forgotpass.component.html',
  styleUrls: ['./forgotpass.component.css']
})
export class ForgotPasswordComponent {
  
  email = '';
  
  constructor(private forgotPassService: ForgotPassService,private notificationsService:NotificationService) {}

  onSubmit() {
    
    this.forgotPassService.sendResetLink(this.email).subscribe({
      next: () => {
        this.notificationsService.show('Password reset link sent to your email.',true);
      },
      error: () => {
        this.notificationsService.show('Failed to send reset link. Please try again later.',false);
      }
    });
  }
}
