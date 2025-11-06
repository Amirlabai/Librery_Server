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
  folders: any[] = [];

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

  showEditPathModal = false;
  editedFilePath = '';
  editPathError = '';
  editPathSuccess = '';

  selectedFile: any = null;

  editModalPath = '';
  modalFolders: any[] = [];   
   

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

         this.folders = this.items.filter(
            (item: any) => item.is_folder || item.isFolder
          );  

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
    }else{
      this.selectedFile = item;
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
    
    if(item.is_folder){
      window.open(`http://localhost:8000/download/folder/${item.path}`, '_blank');
    }else{
      window.open(`http://localhost:8000/download/file/${item.path}`, '_blank');
    }
  }

  deleteItem(item: any) {
  if (!confirm(`Delete ${item.name}?`)) return;

  const currentPathBeforeDelete = this.currentPath;

  this.http.post(
    `http://localhost:8000/delete/${item.path}`,
    {},
    { withCredentials: true }
  ).subscribe({
    
    next: () => {
      this.currentPath = currentPathBeforeDelete;
      this.loadFiles()
    },
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
      }, 5000);
    },
    error: (err) => {
      if (err.status === 429 && err.error?.error) {
        this.suggestionError = err.error.error;

        setTimeout(() => {
          this.suggestionError = '';
        }, 10000);
      } else {
        
        this.suggestionError = 'An unexpected error occurred.';
        setTimeout(() => {
          this.suggestionError = '';
        }, 5000);
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
  openEditPathModal() {
  if (!this.selectedFile) return;               
    this.showEditPathModal = true;
    this.editedFilePath = this.selectedFile.path; 
    this.editPathError = '';
    this.editPathSuccess = '';

    this.editModalPath = '';            
    this.loadFoldersForModal('');       
  }
  closeEditPathModal() {
    this.showEditPathModal = false;
    this.editedFilePath = this.currentPath;
    this.editPathError = '';
    this.editPathSuccess = '';
  }
  editFilePath() {

    this.editedFilePath = this.editedFilePath.trim();

  }
  
  setEditedFilePath(folderPath: string) {
  if (!this.selectedFile?.name) return;

    const cleanFolder = (folderPath || '').replace(/^\/+|\/+$/g, '');
    const fileName = this.selectedFile.name;
    this.editedFilePath = cleanFolder ? `/${cleanFolder}/${fileName}` : `/${fileName}`;
  }
  openFolderInModal(folder: any) {
    const next = (folder.path || '').replace(/^\/+|\/+$/g, '');
    this.loadFoldersForModal(next);

    if (this.selectedFile?.name) {
      this.editedFilePath = `/${next}/${this.selectedFile.name}`;
    }
  }
  goBackInModal() {
    const parts = this.editModalPath.split('/').filter(Boolean);
    parts.pop();
    const up = parts.join('/');
    this.loadFoldersForModal(up);

    if (this.selectedFile?.name) {
      this.editedFilePath = up ? `/${up}/${this.selectedFile.name}` : `/${this.selectedFile.name}`;
    }

  }
  private loadFoldersForModal(path: string = '') {
  const clean = path.replace(/^\/+|\/+$/g, '');
  const url = clean
    ? `http://localhost:8000/browse/${clean}`
    : 'http://localhost:8000/browse';

  this.http.get(url, { withCredentials: true }).subscribe({
    next: (res: any) => {
      const items = res.items || [];
      this.modalFolders = items.filter((i: any) => i.is_folder || i.isFolder);
      
      this.editModalPath = (res.current_path ?? clean) || '';
    },
    error: err => console.error(err)
  });
}
}
