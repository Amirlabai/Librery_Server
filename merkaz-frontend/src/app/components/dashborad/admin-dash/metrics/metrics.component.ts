import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { RouterModule } from '@angular/router'; 
import { AdminDashboardService } from '../../../../services/admin-dashboard.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterModule],
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.css', '../admin-dash-shared.css']
})
export class MetricsComponent {
  logs = [
    { type: 'session', name: 'Session Log (Login/Logout)', description: 'Track user login and failure events.' },
    { type: 'download', name: 'Download Log (File/Folder/Delete)', description: 'Track all file, folder, and delete events.' },
    { type: 'suggestion', name: 'Suggestion Log (User Feedback)', description: 'Records all user suggestions.' },
    { type: 'upload', name: 'Upload Log (Uploads traffic)', description: 'Records all uploads.' },
    { type: 'declined', name: 'Declined Log (Declined Files)', description: 'Records all declined files.' }
  ];

  constructor(private adminDashboardService: AdminDashboardService) {}

  downloadLog(type: string) {
    this.adminDashboardService.downloadLog(type);
  }
  
}
