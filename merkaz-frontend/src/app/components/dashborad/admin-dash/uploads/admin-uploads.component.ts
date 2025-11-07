import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AdminDashboardService, UploadItem } from '../../../../services/admin-dashboard.service';


@Component({
  selector: 'app-admin-uploads',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './admin-uploads.component.html',
  styleUrls: ['./admin-uploads.component.css']
})
export class AdminUploadsComponent {
  uploads: UploadItem[] = [];
  flashMessages: { type: 'success' | 'error'; text: string }[] = [];

  constructor(private adminDashboardService: AdminDashboardService) {}

  ngOnInit() {
    this.loadUploads();
  }

  loadUploads() {
    this.adminDashboardService.loadUploads().subscribe({
      next: (data) => {
        this.uploads = data;
      },
      error: () => {
        this.flashMessages = [{ type: 'error', text: 'Failed to load uploads.' }];
      }
    });
  }

  approve(upload: UploadItem, index: number) {
    this.adminDashboardService.approveUpload(upload.filename, upload.path).subscribe({
      next: () => {
        this.flashMessages = [{ type: 'success', text: `Approved ${upload.filename}` }];
        this.uploads.splice(index, 1); 
      },
      error: () => {
        this.flashMessages = [{ type: 'error', text: `Failed to approve ${upload.filename}` }];
      }
    });
  }

  decline(upload: UploadItem, index: number) {
    if (!confirm('Are you sure you want to decline and delete this item?')) return;

    this.adminDashboardService.declineUpload(upload.filename, upload.path).subscribe({
      next: () => {
        this.flashMessages = [{ type: 'success', text: `Declined ${upload.filename}` }];
        this.uploads.splice(index, 1);
      },
      error: () => {
        this.flashMessages = [{ type: 'error', text: `Failed to decline ${upload.filename}` }];
      }
    });
  }
}
