// upload-file.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { NotificationService } from '../../services/notifications/Notifications.service';
import { UploadProgressService } from '../../services/upload.service';

@Component({
  selector: 'app-upload-content',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
  ],
  templateUrl: './upload-file.component.html',
  styleUrls: ['./upload-file.component.css']
})
export class UploadFileComponent implements OnInit, OnDestroy {

  subpath: string = '';
  selectedFiles: File[] = [];
  selectedFolderFiles: File[] = [];
  isUploadingFile: boolean = false;
  isUploadingFolder: boolean = false;
  uploadFileProgress: number = 0;
  uploadFolderProgress: number = 0;
  uploadSpeed: string = '';
  displayedFilesCount: number = 0;
  displayedFoldersCount: number = 0;
  currentUploadingFile: string = '';
  failedFiles: Array<{ fileName: string, error: any }> = [];
  successfulFiles: string[] = [];

  private uploadStartTime: number = 0;
  private uploadInterval: any;
  private progressUpdateInterval: any;

  constructor(
    private userService: UserService, 
    private route: ActivatedRoute,
    private notificationService: NotificationService,
    private uploadProgressService: UploadProgressService
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if (params['path']) {
        this.subpath = params['path'];
      }
    });
  }

  ngOnDestroy() {
    if (this.uploadInterval) {
      clearInterval(this.uploadInterval);
    }
    if (this.progressUpdateInterval) {
      clearInterval(this.progressUpdateInterval);
    }
  }

  onFileChange(event: any) {
    this.selectedFiles = Array.from(event.target.files);
  }

  onFolderChange(event: any) {
    this.selectedFolderFiles = Array.from(event.target.files);
  }

  getFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  getTotalFileSize(files: File[]): string {
    const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
    return this.getFileSize(totalBytes);
  }

  private updateUploadSpeed(loadedBytes: number): void {
    if (this.uploadStartTime === 0) return;

    const elapsedSeconds = (Date.now() - this.uploadStartTime) / 1000;
    if (elapsedSeconds < 0.5) return;

    const bytesPerSecond = loadedBytes / elapsedSeconds;
    this.uploadSpeed = this.getFileSize(bytesPerSecond) + '/s';
  }

  getUploadedFilesCount(): number {
    if (this.isUploadingFile) {
      return this.displayedFilesCount;
    } else if (this.isUploadingFolder) {
      return this.displayedFoldersCount;
    }
    return 0;
  }

  getEstimatedTimeRemaining(): string {
    if (!this.uploadStartTime || !this.uploadSpeed || 
        (this.uploadFileProgress >= 100 && this.uploadFolderProgress >= 100)) {
      return '';
    }

    const elapsedSeconds = (Date.now() - this.uploadStartTime) / 1000;
    const currentProgress = Math.max(this.uploadFileProgress, this.uploadFolderProgress);
    
    if (currentProgress <= 0 || elapsedSeconds < 2) {
      return '';
    }

    const totalBytes = this.isUploadingFile 
      ? this.selectedFiles.reduce((sum, file) => sum + file.size, 0)
      : this.selectedFolderFiles.reduce((sum, file) => sum + file.size, 0);
    
    const uploadedBytes = (totalBytes * currentProgress) / 100;
    const remainingBytes = totalBytes - uploadedBytes;
    const avgBytesPerSecond = uploadedBytes / elapsedSeconds;

    if (avgBytesPerSecond <= 0) {
      return '';
    }

    const remainingSeconds = Math.ceil(remainingBytes / avgBytesPerSecond);

    if (remainingSeconds < 60) {
      return `${remainingSeconds}s remaining`;
    } else if (remainingSeconds < 3600) {
      const minutes = Math.ceil(remainingSeconds / 60);
      return `${minutes}m remaining`;
    } else {
      const hours = Math.ceil(remainingSeconds / 3600);
      return `${hours}h remaining`;
    }
  }

  private animateFilesCount(targetCount: number, isFolder: boolean = false): void {
    if (this.progressUpdateInterval) {
      clearInterval(this.progressUpdateInterval);
    }

    const currentCount = isFolder ? this.displayedFoldersCount : this.displayedFilesCount;
    
    if (currentCount === targetCount) {
      return;
    }
    
    if (isFolder) {
      this.displayedFoldersCount = targetCount;
    } else {
      this.displayedFilesCount = targetCount;
    }
  }

  private simulateProgress(isFolder: boolean = false): void {
    const files = isFolder ? this.selectedFolderFiles : this.selectedFiles;
    const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
    const totalMB = totalBytes / (1024 * 1024);
    
    const estimatedSeconds = Math.max(2, totalMB / 5);
    const updateInterval = 100;
    const incrementPerUpdate = (95 / (estimatedSeconds * 1000)) * updateInterval;
    
    if (this.uploadInterval) {
      clearInterval(this.uploadInterval);
    }
    
    this.uploadInterval = setInterval(() => {
      const currentProgress = isFolder ? this.uploadFolderProgress : this.uploadFileProgress;
      
      if (currentProgress < 95) {
        const newProgress = Math.min(95, currentProgress + incrementPerUpdate);
        
        if (isFolder) {
          this.uploadFolderProgress = Math.round(newProgress);
        } else {
          this.uploadFileProgress = Math.round(newProgress);
        }
        
        const roundedProgress = Math.round(newProgress);
        let expectedCount = Math.floor((files.length * roundedProgress) / 100);
        
        if (roundedProgress > 5 && expectedCount === 0) {
          expectedCount = 1;
        }
        
        this.animateFilesCount(expectedCount, isFolder);
        
        const loadedBytes = (totalBytes * newProgress) / 100;
        this.updateUploadSpeed(loadedBytes);
      }
    }, updateInterval);
  }

  private resetUploadState(isFolder: boolean = false, keepResults: boolean = false): void {
    if (isFolder) {
      this.isUploadingFolder = false;
      if (!keepResults) {
        this.uploadFolderProgress = 0;
        this.displayedFoldersCount = 0;
      }
    } else {
      this.isUploadingFile = false;
      if (!keepResults) {
        this.uploadFileProgress = 0;
        this.displayedFilesCount = 0;
      }
    }
    
    if (!keepResults) {
      this.uploadSpeed = '';
      this.uploadStartTime = 0;
      this.currentUploadingFile = '';
      this.failedFiles = [];
      this.successfulFiles = [];
    }
    
    if (this.progressUpdateInterval) {
      clearInterval(this.progressUpdateInterval);
    }
    if (this.uploadInterval) {
      clearInterval(this.uploadInterval);
    }
  }

  onSubmitFiles() {
    const input = document.getElementById('fileInput') as HTMLInputElement;
    
    if (this.selectedFiles.length === 0) {
      return;
    }
    
    this.isUploadingFile = true;
    this.uploadFileProgress = 0;
    this.displayedFilesCount = 0;
    this.uploadStartTime = Date.now();
    this.uploadSpeed = '';
    this.currentUploadingFile = '';
    this.failedFiles = [];
    this.successfulFiles = [];

    this.uploadProgressService.startUpload('file', this.selectedFiles.length);
    this.notificationService.show(`Uploading 0 / ${this.selectedFiles.length} files...`, true, true);

    this.userService.uploadFiles(this.selectedFiles, this.subpath).subscribe({
      next: (event) => {
        if (event.type === 'progress') {
          const data = event.data;
          
          this.currentUploadingFile = data.currentFile || '';
          this.uploadFileProgress = data.progress || 0;
          this.displayedFilesCount = data.successfulFiles || 0;
          
          this.notificationService.updateMessage(
            `Uploading ${this.displayedFilesCount} / ${this.selectedFiles.length} files... ${this.uploadFileProgress}%`
          );
          
          this.uploadProgressService.updateProgress({
            progress: this.uploadFileProgress,
            uploadedCount: this.displayedFilesCount,
            currentFile: this.currentUploadingFile,
            speed: this.uploadSpeed,
            timeRemaining: this.getEstimatedTimeRemaining()
          });
          
          if (data.fileSuccess !== undefined) {
            if (!data.fileSuccess && data.error) {
              const existingIndex = this.failedFiles.findIndex(f => f.fileName === data.currentFile);
              if (existingIndex === -1) {
                this.failedFiles.push({ fileName: data.currentFile, error: data.error });
              }
            }
          }
          
          if (this.uploadStartTime > 0 && data.completedFiles > 0) {
            const elapsedSeconds = (Date.now() - this.uploadStartTime) / 1000;
            const totalBytes = this.selectedFiles.reduce((sum, file) => sum + file.size, 0);
            const avgBytesPerFile = totalBytes / this.selectedFiles.length;
            const uploadedBytes = avgBytesPerFile * data.completedFiles;
            if (elapsedSeconds > 0.5) {
              const bytesPerSecond = uploadedBytes / elapsedSeconds;
              this.uploadSpeed = this.getFileSize(bytesPerSecond) + '/s';
            }
          }
          
        } else if (event.type === 'complete') {
          const data = event.data;
          
          this.uploadFileProgress = 100;
          this.displayedFilesCount = data.successfulCount || 0;
          this.successfulFiles = data.successful || [];
          this.failedFiles = data.failed || [];
          
          this.uploadProgressService.completeUpload();
          
          if (this.uploadInterval) {
            clearInterval(this.uploadInterval);
          }
          
          let message = '';
          let isSuccess = true;
          
          if (data.successfulCount > 0 && data.failedCount === 0) {
            message = `✓ Successfully uploaded ${data.successfulCount} file(s)`;
            isSuccess = true;
          } else if (data.successfulCount > 0 && data.failedCount > 0) {
            message = `⚠ Uploaded ${data.successfulCount} file(s), ${data.failedCount} failed`;
            isSuccess = false;
          } else {
            message = '✗ Failed to upload files';
            isSuccess = false;
          }
          
          this.notificationService.updateType(isSuccess);
          this.notificationService.updateMessage(message);
          this.notificationService.clear(1000);
          
          setTimeout(() => {
            this.resetUploadState(false);
            input.value = '';
            this.selectedFiles = [];
          }, 2000);
        }
      },
      error: (err) => {
        this.uploadProgressService.cancelUpload();
        
        let errorMessage = '';
        if (this.successfulFiles.length > 0) {
          errorMessage = `⚠ Upload interrupted: ${this.successfulFiles.length} file(s) uploaded, ${this.selectedFiles.length - this.successfulFiles.length} failed`;
        } else {
          errorMessage = '✗ Failed to upload files';
        }
        
        this.notificationService.updateType(false);
        this.notificationService.updateMessage(errorMessage);
        this.notificationService.clear(1000);
        
        setTimeout(() => {
          this.resetUploadState(false);
          input.value = '';
          this.selectedFiles = [];
        }, 2000);
      }
    });
  }

  onSubmitFolder() {
    const input = document.getElementById('folderInput') as HTMLInputElement;
    
    if (this.selectedFolderFiles.length === 0) {
      return;
    }
    
    this.isUploadingFolder = true;
    this.uploadFolderProgress = 0;
    this.displayedFoldersCount = 0;
    this.uploadStartTime = Date.now();
    this.uploadSpeed = '';
    this.currentUploadingFile = '';
    this.failedFiles = [];
    this.successfulFiles = [];

    this.uploadProgressService.startUpload('folder', this.selectedFolderFiles.length);
    this.notificationService.show(`Uploading 0 / ${this.selectedFolderFiles.length} files...`, true, true);

    this.userService.uploadFiles(this.selectedFolderFiles, this.subpath).subscribe({
      next: (event) => {
        if (event.type === 'progress') {
          const data = event.data;
          
          this.currentUploadingFile = data.currentFile || '';
          this.uploadFolderProgress = data.progress || 0;
          this.displayedFoldersCount = data.successfulFiles || 0;
          
          this.notificationService.updateMessage(
            `Uploading ${this.displayedFoldersCount} / ${this.selectedFolderFiles.length} files... ${this.uploadFolderProgress}%`
          );
          
          this.uploadProgressService.updateProgress({
            progress: this.uploadFolderProgress,
            uploadedCount: this.displayedFoldersCount,
            currentFile: this.currentUploadingFile,
            speed: this.uploadSpeed,
            timeRemaining: this.getEstimatedTimeRemaining()
          });
          
          if (data.fileSuccess !== undefined) {
            if (!data.fileSuccess && data.error) {
              const existingIndex = this.failedFiles.findIndex(f => f.fileName === data.currentFile);
              if (existingIndex === -1) {
                this.failedFiles.push({ fileName: data.currentFile, error: data.error });
              }
            }
          }
          
          if (this.uploadStartTime > 0 && data.completedFiles > 0) {
            const elapsedSeconds = (Date.now() - this.uploadStartTime) / 1000;
            const totalBytes = this.selectedFolderFiles.reduce((sum, file) => sum + file.size, 0);
            const avgBytesPerFile = totalBytes / this.selectedFolderFiles.length;
            const uploadedBytes = avgBytesPerFile * data.completedFiles;
            if (elapsedSeconds > 0.5) {
              const bytesPerSecond = uploadedBytes / elapsedSeconds;
              this.uploadSpeed = this.getFileSize(bytesPerSecond) + '/s';
            }
          }
          
        } else if (event.type === 'complete') {
          const data = event.data;
          
          this.uploadFolderProgress = 100;
          this.displayedFoldersCount = data.successfulCount || 0;
          this.successfulFiles = data.successful || [];
          this.failedFiles = data.failed || [];
          
          this.uploadProgressService.completeUpload();
          
          if (this.uploadInterval) {
            clearInterval(this.uploadInterval);
          }
          
          let message = '';
          let isSuccess = true;
          
          if (data.successfulCount > 0 && data.failedCount === 0) {
            message = `✓ Successfully uploaded ${data.successfulCount} file(s)`;
            isSuccess = true;
          } else if (data.successfulCount > 0 && data.failedCount > 0) {
            message = `⚠ Uploaded ${data.successfulCount} file(s), ${data.failedCount} failed`;
            isSuccess = false;
          } else {
            message = '✗ Failed to upload folder';
            isSuccess = false;
          }
          
          this.notificationService.updateType(isSuccess);
          this.notificationService.updateMessage(message);
          this.notificationService.clear(1000);
          
          setTimeout(() => {
            this.resetUploadState(true);
            input.value = '';
            this.selectedFolderFiles = [];
          }, 2000);
        }
      },
      error: (err) => {
        this.uploadProgressService.cancelUpload();
        
        let errorMessage = '';
        if (this.successfulFiles.length > 0) {
          errorMessage = `⚠ Upload interrupted: ${this.successfulFiles.length} file(s) uploaded, ${this.selectedFolderFiles.length - this.successfulFiles.length} failed`;
        } else {
          errorMessage = '✗ Failed to upload folder';
        }
        
        this.notificationService.updateType(false);
        this.notificationService.updateMessage(errorMessage);
        this.notificationService.clear(1000);
        
        setTimeout(() => {
          this.resetUploadState(true);
          input.value = '';
          this.selectedFolderFiles = [];
        }, 2000);
      }
    });
  }
}