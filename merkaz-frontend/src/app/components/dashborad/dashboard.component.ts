import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import {NgClass} from '@angular/common';
import {FormsModule} from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html',
  imports: [
    NgClass,
    FormsModule,
    CommonModule,
    RouterModule
  ],
  styleUrls: ['./dashboard.component.css']
})


export class DashboardComponent {
  items: any[] = [];
  isAdmin = false;
  userRole = '';
  currentPath = '';
  flashMessages: { type: string, text: string }[] = [];
  cooldownLevel = 0;
  suggestionText = '';
  suggestionSuccess = '';
  suggestionError = '';

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    this.userRole = localStorage.getItem('role') || '';
    this.isAdmin = this.userRole === 'admin';
    this.loadFiles();
  }

  loadFiles() {
  this.http.get('http://localhost:8000/browse', { withCredentials: true }).subscribe({
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
    this.currentPath = ''; 
    this.loadFiles();
  }
  navAdmin(){
    const role = localStorage.getItem('role');
      if (role === 'admin') {
        this.isAdmin = true;
      if (this.isAdmin) {
        this.router.navigate(['/metrics']);
      }
    }
  }


  download(item: any) {
    window.open(`http://localhost:8000/browse/download/${item.path}`, '_blank');
  }

  deleteItem(item: any) {
    if (!confirm(`Delete ${item.name}?`)) return;
    this.http.delete(`http://localhost:8000/browse/delete/${item.path}`).subscribe({
      next: () => this.loadFiles(),
      error: err => console.error(err)
    });
  }

  logout() {
    this.http.post('http://localhost:8000/logout', {}, { withCredentials: true }).subscribe({
      next: () => {
        localStorage.clear();
        this.router.navigate(['/login']);
      },
      error: err => console.error('Logout failed', err)
    });
  }

  submitSuggestion() {
    this.http.post('http://localhost:8000/suggest', { suggestion: this.suggestionText }).subscribe({
      next: () => {
        this.suggestionSuccess = 'Suggestion submitted!';
        this.suggestionText = '';
      },
      error: () => this.suggestionError = 'Failed to send suggestion.'
    });
  }

  
}
