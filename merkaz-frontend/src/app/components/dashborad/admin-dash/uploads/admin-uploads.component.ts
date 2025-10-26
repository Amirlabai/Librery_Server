import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

interface UploadItem {
  timestamp: string;
  email: string;
  filename: string;
  path: string;
}

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

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadUploads();
  }

  loadUploads() {
    this.http.get<UploadItem[]>('http://localhost:8000/admin/uploads', { withCredentials: true }).subscribe({
      next: data => this.uploads = data,
      error: () => this.flashMessages = [{ type: 'error', text: 'Failed to load uploads.' }]
    });
  }

  approve(upload: UploadItem, index: number) {
  const formData = new FormData();
  formData.append('target_path', upload.path);

  this.http.post(`http://localhost:8000/admin/move_upload/${upload.filename}`, formData, {
    withCredentials: true
  }).subscribe({
    next: () => {
      this.flashMessages = [{ type: 'success', text: `Approved ${upload.filename}` }];
      this.uploads.splice(index, 1);
    },
    error: () => this.flashMessages = [{ type: 'error', text: `Failed to approve ${upload.filename}` }]
  });
}

  decline(upload: UploadItem, index: number) {
    
    if (!confirm('Are you sure you want to decline and delete this item?')) return;

    const formData = new FormData();
    formData.append('email', upload.email);

    this.http.post(`http://localhost:8000/admin/decline_upload/${upload.filename}`, formData, {
      withCredentials: true
    }).subscribe({
      next: () => {
        this.flashMessages = [{ type: 'success', text: `Declined ${upload.filename}` }];
        this.uploads.splice(index, 1);
      },
      error: () => this.flashMessages = [{ type: 'error', text: `Failed to decline ${upload.filename}` }]
    });
  }
}
