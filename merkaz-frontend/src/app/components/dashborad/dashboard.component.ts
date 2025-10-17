import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import {NgClass} from '@angular/common';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html',
  imports: [
    NgClass,
    FormsModule
  ],
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  items: any[] = [];
  isAdmin = false;
  currentPath = '';
  flashMessages: { type: string, text: string }[] = [];
  cooldownLevel = 0;
  suggestionText = '';
  suggestionSuccess = '';
  suggestionError = '';

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    this.loadFiles();
  }

  loadFiles() {
    this.http.get('http://localhost:8000/api/files').subscribe({
      next: (res: any) => this.items = res.items || [],
      error: err => console.error(err)
    });
  }

  navigate(item: any) {
    if (item.isFolder) {
      this.currentPath = item.path;
      this.loadFiles();
    } else {
      this.download(item);
    }
  }

  goUp() {

  }

  download(item: any) {
    window.open(`http://localhost:8000/api/download/${item.path}`, '_blank');
  }

  deleteItem(item: any) {
    if (!confirm(`Delete ${item.name}?`)) return;
    this.http.delete(`http://localhost:8000/api/delete/${item.path}`).subscribe({
      next: () => this.loadFiles(),
      error: err => console.error(err)
    });
  }

  logout() {
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }

  submitSuggestion() {
    this.http.post('http://localhost:8000/api/suggest', { suggestion: this.suggestionText }).subscribe({
      next: () => {
        this.suggestionSuccess = 'Suggestion submitted!';
        this.suggestionText = '';
      },
      error: () => this.suggestionError = 'Failed to send suggestion.'
    });
  }
}
