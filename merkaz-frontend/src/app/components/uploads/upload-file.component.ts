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
  currentUploadingFile: string = '';
  failedFiles: Array<{ fileName: string, error: any }> = [];
  successfulFiles: string[] = [];

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

  /**
   * Handle file upload submission
   */
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

    console.log('Starting file upload with', this.selectedFiles.length, 'files');

    this.userService.uploadFiles(this.selectedFiles, this.subpath).subscribe({
      next: (event) => {
        if (event.type === 'progress') {
          const data = event.data;
          
          // Update current file being uploaded
          this.currentUploadingFile = data.currentFile || '';
          
          // Update progress based on actual file completion
          this.uploadFileProgress = data.progress || 0;
          this.displayedFilesCount = data.successfulFiles || 0;
          
          // Update successful and failed file lists
          if (data.fileSuccess !== undefined) {
            if (data.fileSuccess) {
              // File succeeded - already counted in successfulFiles
            } else {
              // File failed - track it
              if (data.error) {
                const existingIndex = this.failedFiles.findIndex(f => f.fileName === data.currentFile);
                if (existingIndex === -1) {
                  this.failedFiles.push({ fileName: data.currentFile, error: data.error });
                }
              }
            }
          }
          
          // Calculate upload speed based on completed files
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
          
          console.log(`Upload progress: ${data.completedFiles}/${data.totalFiles} files, ${data.progress}%`);
        } else if (event.type === 'complete') {
          const data = event.data;
          
          // Update final state
          this.uploadFileProgress = 100;
          this.displayedFilesCount = data.successfulCount || 0;
          this.successfulFiles = data.successful || [];
          this.failedFiles = data.failed || [];
          
          // Clear intervals
          if (this.uploadInterval) {
            clearInterval(this.uploadInterval);
          }
          
          // Show completion message
          let message = '';
          if (data.successfulCount > 0 && data.failedCount === 0) {
            message = `Successfully uploaded ${data.successfulCount} file(s)`;
            this.notificationService.show(message, true);
          } else if (data.successfulCount > 0 && data.failedCount > 0) {
            message = `Uploaded ${data.successfulCount} file(s), ${data.failedCount} failed`;
            this.notificationService.show(message, false);
            console.warn('Failed files:', this.failedFiles);
          } else {
            message = 'Failed to upload files';
            this.notificationService.show(message, false);
            console.error('All files failed:', this.failedFiles);
          }
          
          // Wait a moment to show 100%, then reset
          setTimeout(() => {
            this.resetUploadState(false);
            
            // Reset file input
            input.value = '';
            this.selectedFiles = [];
          }, 2000);
        }
      },
      error: (err) => {
        console.error('Upload error:', err);
        
        // Log error for monitoring
        const errorInfo = {
          timestamp: new Date().toISOString(),
          filesCount: this.selectedFiles.length,
          successfulCount: this.successfulFiles.length,
          error: err
        };
        console.error('Upload error details:', errorInfo);
        
        // Show error message
        if (this.successfulFiles.length > 0) {
          this.notificationService.show(
            `Upload interrupted: ${this.successfulFiles.length} file(s) uploaded, ${this.selectedFiles.length - this.successfulFiles.length} failed`,
            false
          );
        } else {
          this.notificationService.show('Failed to upload files', false);
        }
        
        // Reset state but keep failed files info for potential retry
        setTimeout(() => {
          this.resetUploadState(false);
          input.value = '';
          this.selectedFiles = [];
        }, 2000);
      }
    });
  }

  /**
   * Handle folder upload submission
   */
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

    console.log('Starting folder upload with', this.selectedFolderFiles.length, 'files');

    this.userService.uploadFiles(this.selectedFolderFiles, this.subpath).subscribe({
      next: (event) => {
        if (event.type === 'progress') {
          const data = event.data;
          
          // Update current file being uploaded
          this.currentUploadingFile = data.currentFile || '';
          
          // Update progress based on actual file completion
          this.uploadFolderProgress = data.progress || 0;
          this.displayedFoldersCount = data.successfulFiles || 0;
          
          // Update successful and failed file lists
          if (data.fileSuccess !== undefined) {
            if (data.fileSuccess) {
              // File succeeded
            } else {
              // File failed - track it
              if (data.error) {
                const existingIndex = this.failedFiles.findIndex(f => f.fileName === data.currentFile);
                if (existingIndex === -1) {
                  this.failedFiles.push({ fileName: data.currentFile, error: data.error });
                }
              }
            }
          }
          
          // Calculate upload speed
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
          
          console.log(`Folder upload progress: ${data.completedFiles}/${data.totalFiles} files, ${data.progress}%`);
        } else if (event.type === 'complete') {
          const data = event.data;
          
          // Update final state
          this.uploadFolderProgress = 100;
          this.displayedFoldersCount = data.successfulCount || 0;
          this.successfulFiles = data.successful || [];
          this.failedFiles = data.failed || [];
          
          // Clear intervals
          if (this.uploadInterval) {
            clearInterval(this.uploadInterval);
          }
          
          // Show completion message
          let message = '';
          if (data.successfulCount > 0 && data.failedCount === 0) {
            message = `Successfully uploaded ${data.successfulCount} file(s)`;
            this.notificationService.show(message, true);
          } else if (data.successfulCount > 0 && data.failedCount > 0) {
            message = `Uploaded ${data.successfulCount} file(s), ${data.failedCount} failed`;
            this.notificationService.show(message, false);
            console.warn('Failed files:', this.failedFiles);
          } else {
            message = 'Failed to upload folder';
            this.notificationService.show(message, false);
            console.error('All files failed:', this.failedFiles);
          }
          
          // Wait a moment to show 100%, then reset
          setTimeout(() => {
            this.resetUploadState(true);
            
            // Reset folder input
            input.value = '';
            this.selectedFolderFiles = [];
          }, 2000);
        }
      },
      error: (err) => {
        console.error('Folder upload error:', err);
        
        // Log error for monitoring
        const errorInfo = {
          timestamp: new Date().toISOString(),
          filesCount: this.selectedFolderFiles.length,
          successfulCount: this.successfulFiles.length,
          error: err
        };
        console.error('Folder upload error details:', errorInfo);
        
        // Show error message
        if (this.successfulFiles.length > 0) {
          this.notificationService.show(
            `Upload interrupted: ${this.successfulFiles.length} file(s) uploaded, ${this.selectedFolderFiles.length - this.successfulFiles.length} failed`,
            false
          );
        } else {
          this.notificationService.show('Failed to upload folder', false);
        }
        
        // Reset state
        setTimeout(() => {
          this.resetUploadState(true);
          input.value = '';
          this.selectedFolderFiles = [];
        }, 2000);
      }
    });
  }
}