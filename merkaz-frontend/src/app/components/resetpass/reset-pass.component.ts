import { CommonModule } from "@angular/common";
import { Component, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ActivatedRoute, Router } from "@angular/router";
import { NotificationService } from "../../services/notifications/Notifications.service";
import { AuthService } from "../../services/auth.service";



@Component({
  selector: 'app-reset',
  standalone: true,
  templateUrl: './reset-pass.component.html',
  styleUrls: ['./reset-pass.component.css'],
  imports: [
    CommonModule,
    FormsModule,
  ]
})
export class ResetPassComponent implements OnInit {

    token: string | null = null;
    password = '';
    showPassword = false;

    private passwordPattern =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[{\]};:'",.<>/?]).{8,}$/;

  private emailPattern =
    /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    

    constructor(private route: ActivatedRoute,private router: Router,private notificationsService:NotificationService,private authService: AuthService) {}

    ngOnInit(): void {
        this.token = this.route.snapshot.queryParamMap.get('token');
    }

    onSubmit() {

        if (!this.token) {
            this.notificationsService.show('Invalid reset link', false);
            return;
        }
        if (!this.validateForm()) {
            this.notificationsService.show('Password does not meet requirements', false);
            return;
        }

        this.authService.resetPass(this.token, this.password).subscribe({
        
            next: () => {
                this.notificationsService.show('Password updated successfully', true);
                setTimeout(() => this.router.navigate(['/login']), 1500);
            },
            error: () => {
                this.notificationsService.show('Failed to reset password', false);
            }
        });
    }
    togglePasswordVisibility() {
        this.showPassword = !this.showPassword;
    }

    private validateForm(): boolean {
    
        if (!this.passwordPattern.test(this.password)) {

            this.notificationsService.show('Password must contain at least 8 characters, including uppercase, lowercase, a number, and a special character.',false);
            return false;
        }

        return true;
    }
}