import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface UploadProgress {
  isActive: boolean;
  type: 'file' | 'folder';
  progress: number;
  uploadedCount: number;
  totalCount: number;
  currentFile: string;
  speed: string;
  timeRemaining: string;
}

@Injectable({
  providedIn: 'root'
})
export class UploadProgressService {

  private progressSubject = new BehaviorSubject<UploadProgress>({
    isActive: false,
    type: 'file',
    progress: 0,
    uploadedCount: 0,
    totalCount: 0,
    currentFile: '',
    speed: '',
    timeRemaining: ''
  });

  // Observable that components can subscribe to
  progress$: Observable<UploadProgress> = this.progressSubject.asObservable();

  /**
   * Update the current upload progress
   */
  updateProgress(progress: Partial<UploadProgress>): void {
    const current = this.progressSubject.value;
    this.progressSubject.next({
      ...current,
      ...progress
    });
  }

  /**
   * Start tracking a new upload
   */
  startUpload(type: 'file' | 'folder', totalCount: number): void {
    this.progressSubject.next({
      isActive: true,
      type,
      progress: 0,
      uploadedCount: 0,
      totalCount,
      currentFile: '',
      speed: '',
      timeRemaining: ''
    });
  }

  /**
   * Complete the upload and reset state
   */
  completeUpload(): void {
    const current = this.progressSubject.value;
    this.progressSubject.next({
      ...current,
      isActive: false,
      progress: 100
    });
    
    // Reset after a brief delay to show completion
    setTimeout(() => {
      this.progressSubject.next({
        isActive: false,
        type: 'file',
        progress: 0,
        uploadedCount: 0,
        totalCount: 0,
        currentFile: '',
        speed: '',
        timeRemaining: ''
      });
    }, 2000);
  }

  /**
   * Cancel/reset the upload
   */
  cancelUpload(): void {
    this.progressSubject.next({
      isActive: false,
      type: 'file',
      progress: 0,
      uploadedCount: 0,
      totalCount: 0,
      currentFile: '',
      speed: '',
      timeRemaining: ''
    });
  }

  /**
   * Get current progress state
   */
  getCurrentProgress(): UploadProgress {
    return this.progressSubject.value;
  }
}