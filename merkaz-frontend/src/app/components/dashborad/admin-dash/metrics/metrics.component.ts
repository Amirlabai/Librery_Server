import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router'; 

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterModule],
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.css']
})
export class MetricsComponent {
  logs = [
    { type: 'session', name: 'Session Log (Login/Logout)', description: 'Track user login and failure events.' },
    { type: 'download', name: 'Download Log (File/Folder/Delete)', description: 'Track all file, folder, and delete events.' },
    { type: 'suggestion', name: 'Suggestion Log (User Feedback)', description: 'Records all user suggestions.' },
    { type: 'upload', name: 'Upload Log (Uploads traffic)', description: 'Records all uploads.' },
    { type: 'declined', name: 'Declined Log (Declined Files)', description: 'Records all declined files.' }
  ];

  constructor(private http: HttpClient) {}

  downloadLog(type: string) {
    const url = `http://localhost:8000/admin/metrics/download/${type}`;
    window.open(url, '_blank');
  }
}
