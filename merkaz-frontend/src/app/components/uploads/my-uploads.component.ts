import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

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

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadUploads();
  }

  loadUploads() {
    this.http.get<UploadHistory[]>('http://localhost:8000/my_uploads', { withCredentials: true }).subscribe({
      next: data => this.uploads = data,
      error: err => {
        console.error('Failed to load uploads', err);
        this.uploads = [];
      }
    });
  }
}
