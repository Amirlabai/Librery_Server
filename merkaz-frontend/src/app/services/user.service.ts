import { HttpClient, HttpEvent, HttpEventType, HttpRequest, HttpResponse } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable, of, throwError } from "rxjs";
import { map, catchError, delay, filter, first, tap } from "rxjs/operators";
import { ApiConfigService } from "./api-config.service";

export interface UploadHistory {
  timestamp: string;
  filename: string;
  path: string | null;
  status: 'Pending Review' | 'Declined' | 'Approved';
}


@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(
    private http: HttpClient,
    private apiConfig: ApiConfigService
  ) { }
  
  private get baseUrl(): string {
    return this.apiConfig.getBackendUrl();
  }

  loadUploads(): Observable<UploadHistory[]> {
    return this.http.get<UploadHistory[]>(`${this.baseUrl}/my_uploads`, { withCredentials: true });
  }

  /**
   * Upload a single file with retry logic and progress tracking
   * Returns an observable that emits progress updates and final response
   */
  private uploadSingleFile(file: File, subpath: string, retryCount: number = 3, progressCallback?: (loaded: number, total: number) => void): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subpath', subpath);

    const req = new HttpRequest('POST', `${this.baseUrl}/upload`, formData, {
      reportProgress: true,
      withCredentials: true
    });

    return this.http.request(req).pipe(
      map((event: HttpEvent<any>) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          // Emit progress update via callback
          if (progressCallback) {
            progressCallback(event.loaded, event.total);
          }
          return null; // Return null for progress events
        } else if (event.type === HttpEventType.Response) {
          return event.body; // Return response body for completion
        }
        return null;
      }),
      // Filter out null values (progress events) and only pass through the final response
      filter((result: any) => result !== null),
      first(), // Take only the first (and only) response
      catchError((error) => {
        // Log the error for monitoring
        console.error(`Upload failed for file: ${file.name}`, error);
        
        // Retry on network errors (status 0/undefined) or 500 errors
        const isRetryable = !error.status || error.status === 0 || error.status >= 500;
        
        if (retryCount > 0 && isRetryable) {
          console.log(`Retrying upload for ${file.name}, attempts remaining: ${retryCount}`);
          return this.uploadSingleFile(file, subpath, retryCount - 1, progressCallback).pipe(
            delay(1000 * (4 - retryCount)) // Exponential backoff
          );
        }
        
        // Return error with file info for handling
        return throwError(() => ({
          error,
          fileName: file.name,
          fileSize: file.size
        }));
      })
    );
  }

  /**
   * Upload files individually with progress tracking and retry logic
   * Returns an observable that emits progress updates for each file
   */
  uploadFiles(files: File[], subpath: string): Observable<{ type: 'progress' | 'complete' | 'error', data: any }> {
    return new Observable(observer => {
      let aborted = false;
      let currentSub: { unsubscribe: () => void } | null = null;
      const totalFiles = files.length;
      let completedFiles = 0;
      let successfulFiles: string[] = [];
      let failedFiles: Array<{ fileName: string, error: any }> = [];
      
      // Track total bytes uploaded across all files
      let totalBytesUploaded = 0;
      const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
      const uploadStartTime = Date.now();
      
      // Upload files sequentially to avoid overwhelming the server
      const uploadNext = (index: number) => {
        if (aborted) {
          return;
        }
        if (index >= totalFiles) {
          // All files processed
          observer.next({
            type: 'complete',
            data: {
              successful: successfulFiles,
              failed: failedFiles,
              total: totalFiles,
              successfulCount: successfulFiles.length,
              failedCount: failedFiles.length
            }
          });
          observer.complete();
          return;
        }

        const file = files[index];
        let currentFileBytesUploaded = 0;
        
        // Emit progress update
        observer.next({
          type: 'progress',
          data: {
            currentFile: file.name,
            currentFileIndex: index + 1,
            totalFiles: totalFiles,
            completedFiles: completedFiles,
            successfulFiles: successfulFiles.length,
            failedFiles: failedFiles.length,
            progress: Math.round((completedFiles / totalFiles) * 100),
            bytesUploaded: totalBytesUploaded,
            totalBytes: totalBytes
          }
        });

        // Progress callback to track HTTP upload progress for current file
        const progressCallback = (loaded: number, total: number) => {
          // Calculate bytes uploaded for this file
          const fileBytesUploaded = loaded;
          const previousBytes = currentFileBytesUploaded;
          currentFileBytesUploaded = fileBytesUploaded;
          
          // Update total bytes uploaded (subtract previous, add new)
          totalBytesUploaded = totalBytesUploaded - previousBytes + fileBytesUploaded;
          
          // Calculate overall progress including current file
          const overallProgress = totalBytes > 0 
            ? Math.round((totalBytesUploaded / totalBytes) * 100)
            : Math.round((completedFiles / totalFiles) * 100);
          
          // Emit progress update with real-time bytes
          observer.next({
            type: 'progress',
            data: {
              currentFile: file.name,
              currentFileIndex: index + 1,
              totalFiles: totalFiles,
              completedFiles: completedFiles,
              successfulFiles: successfulFiles.length,
              failedFiles: failedFiles.length,
              progress: overallProgress,
              bytesUploaded: totalBytesUploaded,
              totalBytes: totalBytes,
              currentFileProgress: total > 0 ? Math.round((loaded / total) * 100) : 0,
              isUploading: true // Flag to indicate file is actively uploading
            }
          });
        };

        currentSub = this.uploadSingleFile(file, subpath, 3, progressCallback).subscribe({
          next: (response) => {
            if (aborted) return;
            completedFiles++;
            // Mark this file's bytes as fully uploaded
            totalBytesUploaded = totalBytesUploaded - currentFileBytesUploaded + file.size;
            
            if (response && response.successful_uploads && response.successful_uploads.length > 0) {
              // File uploaded successfully
              successfulFiles.push(...response.successful_uploads);
              
              observer.next({
                type: 'progress',
                data: {
                  currentFile: file.name,
                  currentFileIndex: index + 1,
                  totalFiles: totalFiles,
                  completedFiles: completedFiles,
                  successfulFiles: successfulFiles.length,
                  failedFiles: failedFiles.length,
                  progress: totalBytes > 0 
                    ? Math.round((totalBytesUploaded / totalBytes) * 100)
                    : Math.round((completedFiles / totalFiles) * 100),
                  bytesUploaded: totalBytesUploaded,
                  totalBytes: totalBytes,
                  fileSuccess: true
                }
              });
            } else {
              // File failed but request completed
              failedFiles.push({ fileName: file.name, error: response?.error || 'Upload failed' });
              
              observer.next({
                type: 'progress',
                data: {
                  currentFile: file.name,
                  currentFileIndex: index + 1,
                  totalFiles: totalFiles,
                  completedFiles: completedFiles,
                  successfulFiles: successfulFiles.length,
                  failedFiles: failedFiles.length,
                  progress: totalBytes > 0 
                    ? Math.round((totalBytesUploaded / totalBytes) * 100)
                    : Math.round((completedFiles / totalFiles) * 100),
                  bytesUploaded: totalBytesUploaded,
                  totalBytes: totalBytes,
                  fileSuccess: false
                }
              });
            }
            
            // Continue with next file
            uploadNext(index + 1);
          },
          error: (error) => {
            completedFiles++;
            // Remove partial upload bytes if file failed
            totalBytesUploaded -= currentFileBytesUploaded;
            
            failedFiles.push({ 
              fileName: file.name, 
              error: error.error || error.message || 'Network error' 
            });
            
            observer.next({
              type: 'progress',
              data: {
                currentFile: file.name,
                currentFileIndex: index + 1,
                totalFiles: totalFiles,
                completedFiles: completedFiles,
                successfulFiles: successfulFiles.length,
                failedFiles: failedFiles.length,
                progress: totalBytes > 0 
                  ? Math.round((totalBytesUploaded / totalBytes) * 100)
                  : Math.round((completedFiles / totalFiles) * 100),
                bytesUploaded: totalBytesUploaded,
                totalBytes: totalBytes,
                fileSuccess: false,
                error: error.error || error.message
              }
            });
            
            // Continue with next file even if this one failed
            uploadNext(index + 1);
          }
        });
      };

      uploadNext(0);

      return () => {
        aborted = true;
        if (currentSub) {
          currentSub.unsubscribe();
        }
      };
    });
  }

  // uploadFolder is now handled by uploadFiles - kept for backward compatibility if needed
  uploadFolder(files: File[], subpath: string): Observable<{ type: 'progress' | 'complete' | 'error', data: any }> {
    return this.uploadFiles(files, subpath);
  }

}
