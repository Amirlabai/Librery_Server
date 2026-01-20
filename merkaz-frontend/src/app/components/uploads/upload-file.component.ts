import { Component, OnInit, OnDestroy } from '@angular/core';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { NotificationService } from '../../services/notifications/Notifications.service';

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

  private uploadStartTime: number = 0;
  private uploadInterval: any;
  private progressUpdateInterval: any;

  constructor(
    private userService: UserService, 
    private route: ActivatedRoute,
    private notificationService: NotificationService
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if (params['path']) {
        this.subpath = params['path'];
      }
    });
  }

  ngOnDestroy() {
    // Clean up intervals when component is destroyed
    if (this.uploadInterval) {
      clearInterval(this.uploadInterval);
    }
    if (this.progressUpdateInterval) {
      clearInterval(this.progressUpdateInterval);
    }
  }

  onFileChange(event: any) {
    this.selectedFiles = Array.from(event.target.files);
    console.log('Files selected:', this.selectedFiles.length);
  }

  onFolderChange(event: any) {
    this.selectedFolderFiles = Array.from(event.target.files);
    console.log('Folder files selected:', this.selectedFolderFiles.length);
  }

  /**
   * Helper method to format file size in human readable format
   * Converts bytes to appropriate unit (Bytes, KB, MB, GB)
   */
  getFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Helper method to calculate total size of all selected files
   */
  getTotalFileSize(files: File[]): string {
    const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
    return this.getFileSize(totalBytes);
  }

  /**
   * Calculate upload speed based on progress
   * Updates the uploadSpeed property with current transfer rate
   */
  private updateUploadSpeed(loadedBytes: number): void {
    if (this.uploadStartTime === 0) return;

    const elapsedSeconds = (Date.now() - this.uploadStartTime) / 1000;
    if (elapsedSeconds < 0.5) return; // Wait at least 0.5 seconds before calculating speed

    const bytesPerSecond = loadedBytes / elapsedSeconds;
    this.uploadSpeed = this.getFileSize(bytesPerSecond) + '/s';
  }

  /**
   * Calculate how many files have been uploaded based on progress percentage
   */
  getUploadedFilesCount(): number {
    if (this.isUploadingFile) {
      return this.displayedFilesCount;
    } else if (this.isUploadingFolder) {
      return this.displayedFoldersCount;
    }
    return 0;
  }

  /**
   * Calculate estimated time remaining based on current upload speed and progress
   */
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

    // Calculate average speed and estimate remaining time
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

  /**
   * Update the displayed files count to match the target count
   * This provides real-time feedback on how many files have been processed
   */
  private animateFilesCount(targetCount: number, isFolder: boolean = false): void {
    // Clear any existing interval
    if (this.progressUpdateInterval) {
      clearInterval(this.progressUpdateInterval);
    }

    // Get current count
    const currentCount = isFolder ? this.displayedFoldersCount : this.displayedFilesCount;
    
    // If target is same as current, no need to animate
    if (currentCount === targetCount) {
      return;
    }
    
    // Update immediately to target count
    if (isFolder) {
      this.displayedFoldersCount = targetCount;
    } else {
      this.displayedFilesCount = targetCount;
    }
  }

  /**
   * Simulate upload progress since Flask doesn't report real-time progress
   * Shows gradual progress to give user feedback that upload is active
   */
  private simulateProgress(isFolder: boolean = false): void {
    // Calculate total size to estimate upload time
    const files = isFolder ? this.selectedFolderFiles : this.selectedFiles;
    const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
    const totalMB = totalBytes / (1024 * 1024);
    
    // Estimate time based on file size (assume ~5 MB/s upload speed)
    const estimatedSeconds = Math.max(2, totalMB / 5);
    const updateInterval = 100; // Update every 100ms
    const incrementPerUpdate = (95 / (estimatedSeconds * 1000)) * updateInterval; // Stop at 95%
    
    // Clear any existing interval
    if (this.uploadInterval) {
      clearInterval(this.uploadInterval);
    }
    
    // Start progress simulation
    this.uploadInterval = setInterval(() => {
      const currentProgress = isFolder ? this.uploadFolderProgress : this.uploadFileProgress;
      
      // Stop at 95% - the rest will complete when server responds
      if (currentProgress < 95) {
        const newProgress = Math.min(95, currentProgress + incrementPerUpdate);
        
        if (isFolder) {
          this.uploadFolderProgress = Math.round(newProgress); // Round to integer
        } else {
          this.uploadFileProgress = Math.round(newProgress); // Round to integer
        }
        
        // Update file count based on progress (at least 1 file if progress > 0)
        const roundedProgress = Math.round(newProgress);
        let expectedCount = Math.floor((files.length * roundedProgress) / 100);
        
        // Show at least 1 file uploaded once we're past 5%
        if (roundedProgress > 5 && expectedCount === 0) {
          expectedCount = 1;
        }
        
        this.animateFilesCount(expectedCount, isFolder);
        
        // Calculate simulated speed
        const loadedBytes = (totalBytes * newProgress) / 100;
        this.updateUploadSpeed(loadedBytes);
      }
    }, updateInterval);
  }

  /**
   * Reset upload state after completion or error
   */
  private resetUploadState(isFolder: boolean = false): void {
    if (isFolder) {
      this.isUploadingFolder = false;
      this.uploadFolderProgress = 0;
      this.displayedFoldersCount = 0;
    } else {
      this.isUploadingFile = false;
      this.uploadFileProgress = 0;
      this.displayedFilesCount = 0;
    }
    
    this.uploadSpeed = '';
    this.uploadStartTime = 0;
    
    if (this.progressUpdateInterval) {
      clearInterval(this.progressUpdateInterval);
    }
    if (this.uploadInterval) {
      clearInterval(this.uploadInterval);
    }
  }

  /**
   * Handle file upload submission
   */
  onSubmitFiles() {
    const input = document.getElementById('fileInput') as HTMLInputElement;
    
    this.isUploadingFile = true;
    this.uploadFileProgress = 0;
    this.displayedFilesCount = 0;
    this.uploadStartTime = Date.now();
    this.uploadSpeed = '';

    console.log('Starting file upload with', this.selectedFiles.length, 'files');

    // Start simulated progress since Flask doesn't support real-time progress
    this.simulateProgress();

    this.userService.uploadFiles(this.selectedFiles, this.subpath).subscribe({
      next: (progress) => {
        console.log('Progress event received:', progress, 'type:', typeof progress);
        
        // Check if it's a progress number or the final response
        if (typeof progress === 'number') {
          console.log('Progress percentage:', progress);
          this.uploadFileProgress = Math.min(progress, 100); // Cap at 100%
          
          // Calculate expected file count and update it
          const expectedCount = Math.floor((this.selectedFiles.length * progress) / 100);
          console.log('Expected count:', expectedCount, 'out of', this.selectedFiles.length);
          this.animateFilesCount(expectedCount, false);
          
          // Calculate total bytes uploaded based on progress percentage
          const totalBytes = this.selectedFiles.reduce((sum, file) => sum + file.size, 0);
          const loadedBytes = (totalBytes * progress) / 100;
          this.updateUploadSpeed(loadedBytes);
        } else {
          // This is the final response, upload is complete
          console.log('Upload complete!');
          
          // Jump to 100% before resetting
          this.uploadFileProgress = 100;
          this.animateFilesCount(this.selectedFiles.length, false);
          
          // Clear simulation interval
          if (this.uploadInterval) {
            clearInterval(this.uploadInterval);
          }
          
          // Wait a moment to show 100%, then reset
          setTimeout(() => {
            this.resetUploadState(false);
            this.notificationService.show('Files uploaded successfully', true);  
            
            // Reset file input
            input.value = '';
            this.selectedFiles = [];
          }, 500);
        }
      },
      error: (err) => {
        console.error('Upload error:', err);
        this.resetUploadState(false);
        this.notificationService.show('Failed to upload files', false);
        
        // Reset file input
        input.value = '';
        this.selectedFiles = [];
      }
    });
  }

  /**
   * Handle folder upload submission
   */
  onSubmitFolder() {
    const input = document.getElementById('folderInput') as HTMLInputElement;
    
    this.isUploadingFolder = true;
    this.uploadFolderProgress = 0;
    this.displayedFoldersCount = 0;
    this.uploadStartTime = Date.now();
    this.uploadSpeed = '';

    console.log('Starting folder upload with', this.selectedFolderFiles.length, 'files');

    // Start simulated progress since Flask doesn't support real-time progress
    this.simulateProgress(true);

    this.userService.uploadFiles(this.selectedFolderFiles, this.subpath).subscribe({
      next: (progress) => {
        // Check if it's a progress number or the final response
        if (typeof progress === 'number') {
          this.uploadFolderProgress = Math.min(progress, 100); // Cap at 100%
          
          // Calculate expected file count and update it
          const expectedCount = Math.floor((this.selectedFolderFiles.length * progress) / 100);
          this.animateFilesCount(expectedCount, true);
          
          // Calculate total bytes uploaded based on progress percentage
          const totalBytes = this.selectedFolderFiles.reduce((sum, file) => sum + file.size, 0);
          const loadedBytes = (totalBytes * progress) / 100;
          this.updateUploadSpeed(loadedBytes);
        } else {
          // This is the final response, upload is complete
          console.log('Folder upload complete!');
          
          // Jump to 100% before resetting
          this.uploadFolderProgress = 100;
          this.animateFilesCount(this.selectedFolderFiles.length, true);
          
          // Clear simulation interval
          if (this.uploadInterval) {
            clearInterval(this.uploadInterval);
          }
          
          // Wait a moment to show 100%, then reset
          setTimeout(() => {
            this.resetUploadState(true);
            this.notificationService.show('Folder uploaded successfully', true);
            
            // Reset folder input
            input.value = '';
            this.selectedFolderFiles = [];
          }, 500);
        }
      },
      error: (err) => {
        console.error('Folder upload error:', err);
        this.resetUploadState(true);
        this.notificationService.show('Failed to upload folder', false);
        
        // Reset folder input
        input.value = '';
        this.selectedFolderFiles = [];
      }
    });
  }
}