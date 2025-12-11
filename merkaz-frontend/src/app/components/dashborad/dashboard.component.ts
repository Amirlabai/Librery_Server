import { Component } from '@angular/core';
import { Router } from '@angular/router';
import {NgClass} from '@angular/common';
import {FormsModule} from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardService } from '../../services/dashboard.service';
import { NotificationService } from '../../services/notifications/Notifications.service';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { MatIcon } from "@angular/material/icon";

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html',
  imports: [
    NgClass,
    FormsModule,
    CommonModule,
    RouterModule,
    MatIcon
],
  styleUrls: ['./dashboard.component.css']
})


export class DashboardComponent {
  items: any[] = [];
  folders: any[] = [];
  allItems: any[] = [];
  private searchSubject = new Subject<string>();
  isSearching = false;

  userFullName: string | null = null;
  isAdmin = false;
  userRole = '';
  currentPath = '';
  
  cooldownLevel = 0;
  suggestionText = '';
  
  showCreateFolderModal = false;
  newFolderName = '';
  
  showEditPathModal = false;
  editedFilePath = '';

  showDonwloadWarningModal = false;
  downloadItem = '';

  showSuggestBox = false;
  showUsefulLinksModal = false;
  
  selectedFile: any = null;

  editModalPath = '';
  modalFolders: any[] = [];   

  searchFiles: string = '';
  
  previewFile: any = null;
  previewUrl: string = '';

  oldPath: string = '';


  constructor(
    private dashboardService: DashboardService,
    private router: Router,
    private notificationService: NotificationService,
  ) {}

  ngOnInit() {
    this.userRole = localStorage.getItem('role') || '';
    this.isAdmin = this.userRole === 'admin';
    this.loadFiles();
    this.getUserFullName();


    this.searchSubject
    .pipe(
      debounceTime(100),
      distinctUntilChanged()
    )
    .subscribe(value => {
      this.executeSearch(value);   
    });

  }

  loadFiles() {
    this.dashboardService.loadFiles(this.currentPath).subscribe({
      next: (res: any) => {
        const files = res.files || [];
        const folders = res.folders || [];

        this.items = [...folders, ...files];
        this.allItems = [...this.items]; 

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


  preview(item: any, event: Event) {
    event.stopPropagation();
    if (item.is_folder || item.isFolder) {
      return;
    }
    this.previewFile = item;
    this.previewUrl = this.dashboardService.getPreviewUrl(item);
    window.open(this.previewUrl);
  }

  isImageFile(filename: string): boolean {
    const ext = filename.toLowerCase().split('.').pop();
    return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(ext || '');
  }

  isVideoFile(filename: string): boolean {
    const ext = filename.toLowerCase().split('.').pop();
    return ['mp4', 'mov', 'avi', 'mkv', 'webm', 'ogg'].includes(ext || '');
  }

  isPdfFile(filename: string): boolean {
    return filename.toLowerCase().endsWith('.pdf');
  }

  isTextFile(filename: string): boolean {
    const ext = filename.toLowerCase().split('.').pop();
    return ['txt', 'md', 'json', 'xml', 'csv', 'log', 'html', 'css', 'js', 'ts'].includes(ext || '');
  }

  download(event: Event) {
    event.stopPropagation();
    
    const url = this.dashboardService.getDownloadUrl(this.downloadItem);
    window.open(url, '_blank');
  }

  deleteItem(item: any,event: MouseEvent) {

    event.stopPropagation();
    if (!confirm(`Delete ${item.name}?`)) return;

    const currentPathBeforeDelete = this.currentPath;

    this.dashboardService.deleteItem(item.path).subscribe({
      next: () => {
        this.currentPath = currentPathBeforeDelete;
        this.notificationService.show('Deleted successfully',true);
        this.loadFiles();  
      },
      error: () => {
        this.notificationService.show('Failed to delete item',false);
      }
    });
  }

  logout() {

    this.dashboardService.logout().subscribe({
      next: () => {
        localStorage.clear();
        this.router.navigate(['/login']);
        this.notificationService.show('Logout successfuly',true);
      },
      error: (err) => {
        this.notificationService.show('Logout failed',false);
      }
    });
  }

  async submitSuggestion() {
    if (!this.suggestionText.trim()) {
      this.notificationService.show('Suggestion cannot be empty',false)
      return;
    }

    this.dashboardService.submitSuggestion(this.suggestionText).subscribe({
      next: () => {
        this.notificationService.show('Suggestion submited!',true)
        this.suggestionText = '';

        this.closeSuggestBox();
      },
      error: (err) => {
        if (err.status === 429 && err.error?.error) {

          this.notificationService.show(err.error.error,false)
          
        } else {

          this.notificationService.show('An unexpected error occurred.',false);
        }
      }
    });
  }

  openCreateFolderModal() {
    this.showCreateFolderModal = true;
    this.newFolderName = '';
  }

  closeCreateFolderModal() {
    this.showCreateFolderModal = false;
    this.newFolderName = '';
  }
  closeDonwloadWarningModal(){
    this.showDonwloadWarningModal = false;
  }
  openDonwloadWarningModal(item: any, event: Event){
    event.stopPropagation();
    this.showDonwloadWarningModal = true;
    this.downloadItem = item;
    
  }

  createFolder() {

    const folderName = this.newFolderName.trim();

    if (!folderName) {
      this.notificationService.show('Folder name cannot be empty.',false)
      return;
    }

    this.dashboardService.createFolder(this.currentPath, folderName).subscribe({
      next: (res: any) => {

        if (res.message) {
          this.notificationService.show(res.message,true)
          this.closeCreateFolderModal();
          this.loadFiles();
        }
      },
      error: () => {
        this.notificationService.show('Failed to create folder.',false)
      }
    });
  }

  goToRoot() {
    this.currentPath = '';
    this.loadFiles();
  }

  openEditPathModal(item:any, $event:any) {
    $event.stopPropagation();

    this.selectedFile = item;
    this.oldPath = item.path;
    
    if (!this.selectedFile) return;
    
      this.showEditPathModal = true;
      this.editedFilePath = this.selectedFile.path; 
      this.editModalPath = '';            
      this.loadFoldersForModal('');       
  }
  closeEditPathModal() {
    this.showEditPathModal = false;
    this.editedFilePath = this.currentPath;
  }
  editFilePath() {
    if (!this.selectedFile?.upload_id) {
      this.notificationService.show('No file selected.',false)
      return;
    }

    const uploadId = this.selectedFile.upload_id;
    const newPath = this.editedFilePath;
    
    this.dashboardService.editFilePath(uploadId, newPath, this.oldPath).subscribe({
      next: () => {
        this.notificationService.show('Path updated successfully.',true)
        this.closeEditPathModal();
        this.loadFiles();
      },
      error: () => {
        this.notificationService.show('Failed to update path.',false)
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
      error: (err) => {
        this.notificationService.show(`Failed to load folders for modal: ${err.message || err}`, false);
      }
    });
  }
  
  onSearchChange() {
    this.isSearching = true; 
    this.searchSubject.next(this.searchFiles);
  }

  private executeSearch(query: string) {

    if (!query.trim()) {
      this.loadFiles();  
      this.isSearching = false;
      return;
    }
    this.dashboardService.searchFiles(query,this.currentPath).subscribe({
      next: res => {
        const folders = res.folders || [];
        const files = res.files || [];
        this.allItems = [...folders, ...files];
        this.isSearching = false;
      },
      error: err => {
        this.notificationService.show(`search error: ${err}`, false);
        this.isSearching = false; 
      }
    });
  }
  private getUserFullName(){
    const userFullNameLoad = localStorage.getItem('fullName');

    if(userFullNameLoad){
      this.userFullName = userFullNameLoad;
    }
  }
  openSuggestBox(){
    this.showSuggestBox = true;
  }
  closeSuggestBox() {
    this.showSuggestBox = false;
  }
  openUsefulLinksModal(){
    this.showUsefulLinksModal = true;
  }
  closeUsefulLinksModal() {
    this.showUsefulLinksModal = false;
  }

  formatSize(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }
}
