import { Component } from '@angular/core';
import { Router } from '@angular/router';
import {NgClass} from '@angular/common';
import {FormsModule} from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardService } from '../../services/dashboard.service';

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
  private originalItems: any[] = [];
  allItems: any[] = [];

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

  searchFiles: string = '';
   

  constructor(private dashboardService: DashboardService,private router: Router) {}

  ngOnInit() {
    this.userRole = localStorage.getItem('role') || '';
    this.isAdmin = this.userRole === 'admin';
    this.loadFiles();
  }

  loadFiles() {
    this.dashboardService.loadFiles(this.currentPath).subscribe({
      next: (res: any) => {
        const files = res.files || [];
        const folders = res.folders || [];

        this.items = [...folders, ...files];

        if (res.current_path) this.currentPath = res.current_path;
        if (res.is_admin !== undefined) this.isAdmin = res.is_admin;
        if (res.cooldown_level !== undefined) this.cooldownLevel = res.cooldown_level;
      },
      error: (err) => console.error(err)
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
    const url = this.dashboardService.getDownloadUrl(item);
    window.open(url, '_blank');
  }

  deleteItem(item: any) {
    if (!confirm(`Delete ${item.name}?`)) return;

    const currentPathBeforeDelete = this.currentPath;

    this.dashboardService.deleteItem(item.path).subscribe({
      next: () => {
        this.currentPath = currentPathBeforeDelete;
        this.loadFiles();  
      },
      error: (err) => {
        console.error('Failed to delete item:', err);
      }
    });
  }

  logout() {

    this.dashboardService.logout().subscribe({
      next: () => {
        localStorage.clear();
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.error('Logout failed:', err);
      }
    });
  }

  async submitSuggestion() {
    if (!this.suggestionText.trim()) {
      this.suggestionError = 'Suggestion cannot be empty.';
      setTimeout(() => (this.suggestionError = ''), 3000);
      return;
    }

    this.dashboardService.submitSuggestion(this.suggestionText).subscribe({
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
          setTimeout(() => (this.suggestionError = ''), 10000);
        } else {
          this.suggestionError = 'An unexpected error occurred.';
          setTimeout(() => (this.suggestionError = ''), 5000);
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

    const folderName = this.newFolderName.trim();

    if (!folderName) {
      this.folderCreationError = 'Folder name cannot be empty.';
      return;
    }

    this.folderCreationError = '';
    this.folderCreationSuccess = '';

    this.dashboardService.createFolder(this.currentPath, folderName).subscribe({
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
        this.folderCreationError = err.error?.error || 'Failed to create folder.';
      }
    });
  }

  goToRoot() {
    this.currentPath = '';
    this.loadFiles();
  }

  openEditPathModal() {
  
    console.log('edited file:' , this.selectedFile)

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
    if (!this.selectedFile?.upload_id) {
      this.editPathError = 'No file selected.';
      return;
    }

    const uploadId = this.selectedFile.upload_id;
    const newPath = this.editedFilePath.trim();

    console.log('Editing file path:', { uploadId, newPath });

    if (!newPath) {
      this.editPathError = 'New path cannot be empty.';
      return;
    }

    this.dashboardService.editFilePath(uploadId, newPath).subscribe({
      next: (res: any) => {
        this.editPathSuccess = res.message || 'Path updated successfully.';
        setTimeout(() => {
          this.showEditPathModal = false;
          this.loadFiles();
        }, 1000);
      },
      error: (err: any) => {
        this.editPathError = err.error?.error || 'Failed to update path.';
      }
    });
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
    this.dashboardService.browse(path).subscribe({
      next: (res: any) => {
        const folders = res.folders || [];
        this.modalFolders = folders;
        this.editModalPath = (res.current_path ?? path.replace(/^\/+|\/+$/g, '')) || '';
      },
      error: (err) => console.error('Failed to load folders for modal:', err)
    });
  }
  public async onSearchChange() {
    const input = this.searchFiles.trim().toLowerCase();

    if (!input) {
      this.items = [...this.originalItems];
      return;
    }

    if (this.allItems.length === 0) {
      await this.loadAllRecursively('');
    }

    this.items = this.allItems.filter(item => {
      const nameMatch = item.name?.toLowerCase().includes(input);
      const pathMatch = item.path?.toLowerCase().includes(input);
      return nameMatch || pathMatch;
    });

    this.items.sort((a, b) => {
      if (a.is_folder && !b.is_folder) return -1;
      if (!a.is_folder && b.is_folder) return 1;
      return a.name.localeCompare(b.name);
    });
  }
  private async loadAllRecursively(path: string) {
  
    try {
      const res: any = await this.dashboardService.loadFiles(path).toPromise();
      const folders = res.folders || [];
      const files = res.files || [];

      this.allItems.push(...folders, ...files);

      
      for (const folder of folders) {
        await this.loadAllRecursively(folder.path);
      }
    } catch (err) {
      console.error('Recursive load error:', err);
    }
  }
  
}
