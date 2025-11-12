import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AdminDashboardService, UploadItem } from '../../../../services/admin-dashboard.service';
import { NotificationService } from '../../../../services/notifications/Notifications.service';


@Component({
  selector: 'app-admin-uploads',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './admin-uploads.component.html',
  styleUrls: ['./admin-uploads.component.css']
})
export class AdminUploadsComponent {
  
  uploads: UploadItem[] = [];

  constructor(private adminDashboardService: AdminDashboardService,private notificationService:NotificationService) {}

  ngOnInit() {
    this.loadUploads();
  }

  loadUploads() {
    this.adminDashboardService.loadUploads().subscribe({
      next: (data) => {
        this.uploads = data;
      },
      error: () => {
        this.notificationService.show('Failed to load uploads.',false);
      }
    });
  }

  approve(upload: UploadItem, index: number) {

    this.adminDashboardService.approveUpload(upload.filename, upload.path).subscribe({

      next: () => {
        this.notificationService.show(`Approved ${upload.filename}`,true);
        this.uploads.splice(index, 1); 
      },
      error: () => {
        this.notificationService.show(`Failed to approve ${upload.filename}`,false);
      }
    });
  }

  decline(upload: UploadItem, index: number) {
    if (!confirm('Are you sure you want to decline and delete this item?')) return;

    this.adminDashboardService.declineUpload(upload.filename, upload.path).subscribe({
      next: () => {

        this.notificationService.show(`Declined ${upload.filename}`,false);
        this.uploads.splice(index, 1);

      },
      error: () => {
        this.notificationService.show(`Failed to decline ${upload.filename}`,false);
      }
    });
  }
}
