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
  showCreateFolderModal = false;
  newFolderName = '';
  folderCreationError = '';
  folderCreationSuccess = '';
  
  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    this.userRole = localStorage.getItem('role') || '';
    this.isAdmin = this.userRole === 'admin';
    this.loadFiles();
  }

  loadFiles() {
    const url = this.currentPath 
      ? `http://localhost:8000/browse/${this.currentPath}`
      : 'http://localhost:8000/browse';
    
    this.http.get(url, { withCredentials: true }).subscribe({
      next: (res: any) => {
        this.items = res.items || [];
        if (res.current_path !== undefined) {
          this.currentPath = res.current_path;
        }
        if (res.is_admin !== undefined) {
          this.isAdmin = res.is_admin;
        }
        if (res.cooldown_level !== undefined) {
          this.cooldownLevel = res.cooldown_level;
        }
      },
      error: err => console.error(err)
    });
  }

  navigate(item: any) {
    if (item.is_folder || item.isFolder) {
      this.currentPath = item.path;
      this.loadFiles();
    } else {
      this.download(item);
    }
  }
  goUp() {
    const pathParts = this.currentPath.split('/').filter(p => p);
    if (pathParts.length > 0) {
      pathParts.pop();
      this.currentPath = pathParts.join('/');
    } else {
      this.currentPath = '';
    }
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
    window.open(`http://localhost:8000/download/file/${item.path}`, '_blank');
  }

  deleteItem(item: any) {
  if (!confirm(`Delete ${item.name}?`)) return;

  this.http.post(
    `http://localhost:8000/delete/${item.path}`,
    {},
    { withCredentials: true }
  ).subscribe({
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

  async submitSuggestion() {
  this.http.post('http://localhost:8000/suggest',
    { suggestion: this.suggestionText },
    { withCredentials: true }
  ).subscribe({
    next: () => {
      this.suggestionSuccess = 'Suggestion submitted!';
      this.suggestionText = '';

      setTimeout(() => {
        this.suggestionSuccess = '';
        this.ngOnInit();  
      }, 2000);
    },
    error: (err) => {
      if (err.status === 429 && err.error?.error) {
        this.suggestionError = err.error.error; 
      } 
    }
  });
}

  openCreateFolderModal() {
    this.showCreateFolderModal = true;
    this.newFolderName = '';
    this.folderCreationError = '';
    this.folderCreationSuccess = '';
  }

  closeCreateFolderModal() {
    this.showCreateFolderModal = false;
    this.newFolderName = '';
    this.folderCreationError = '';
    this.folderCreationSuccess = '';
  }

  createFolder() {
    if (!this.newFolderName.trim()) {
      this.folderCreationError = 'Folder name cannot be empty.';
      return;
    }

    this.folderCreationError = '';
    this.folderCreationSuccess = '';

    this.http.post(
      'http://localhost:8000/create_folder',
      {
        parent_path: this.currentPath,
        folder_name: this.newFolderName.trim()
      },
      { withCredentials: true }
    ).subscribe({
      next: (res: any) => {
        if (res.message) {
          this.folderCreationSuccess = res.message;
          setTimeout(() => {
            this.closeCreateFolderModal();
            this.loadFiles();
          }, 1000);
        }
      },
      error: (err: any) => {
        if (err.error && err.error.error) {
          this.folderCreationError = err.error.error;
        } else {
          this.folderCreationError = 'Failed to create folder.';
        }
      }
    });
  }
  goToRoot() {
  this.currentPath = '';
  this.loadFiles();
}
  
}
