import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { UserService } from '../../services/user.service';
import { NotificationService } from '../../services/notifications/Notifications.service';

interface UploadHistory {
  timestamp: string;
  filename: string;
  path: string | null;
  status: 'Pending Review' | 'Declined' | 'Approved';
}

@Component({
  selector: 'app-my-uploads',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './my-uploads.component.html',
  styleUrls: ['./my-uploads.component.css']
})
export class MyUploadsComponent {

  uploads: UploadHistory[] = [];
  errorMessage = '';

  constructor(private userService: UserService,private notificationService:NotificationService) {}

  ngOnInit() {
    this.loadUploads();
  }

  loadUploads() {
    this.userService.loadUploads().subscribe({
      next: (data) => {
        this.uploads = data;
      },
      error: () => {

        this.notificationService.show('Failed to load uploads. Please try again later.',false)
        this.uploads = [];
      }
    });
  }
}
