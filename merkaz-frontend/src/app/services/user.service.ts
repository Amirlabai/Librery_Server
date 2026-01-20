import { HttpClient, HttpEvent, HttpEventType, HttpRequest, HttpResponse } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable, of, throwError } from "rxjs";
import { map, catchError, delay, filter, first } from "rxjs/operators";
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
   * Upload a single file with retry logic
   */
  private uploadSingleFile(file: File, subpath: string, retryCount: number = 3): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subpath', subpath);

    const req = new HttpRequest('POST', `${this.baseUrl}/upload`, formData, {
      reportProgress: true,
      withCredentials: true
    });

    return this.http.request(req).pipe(
      // Filter to only get the final response event
      filter((event: HttpEvent<any>): event is HttpResponse<any> => event.type === HttpEventType.Response),
      map((event: HttpResponse<any>) => event.body),
      first(), // Take only the first (and only) response
      catchError((error) => {
        // Log the error for monitoring
        console.error(`Upload failed for file: ${file.name}`, error);
        
        // Retry on network errors (status 0/undefined) or 500 errors
        const isRetryable = !error.status || error.status === 0 || error.status >= 500;
        
        if (retryCount > 0 && isRetryable) {
          console.log(`Retrying upload for ${file.name}, attempts remaining: ${retryCount}`);
          return this.uploadSingleFile(file, subpath, retryCount - 1).pipe(
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
      const totalFiles = files.length;
      let completedFiles = 0;
      let successfulFiles: string[] = [];
      let failedFiles: Array<{ fileName: string, error: any }> = [];
      
      // Upload files sequentially to avoid overwhelming the server
      const uploadNext = (index: number) => {
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
            progress: Math.round((completedFiles / totalFiles) * 100)
          }
        });

        this.uploadSingleFile(file, subpath).subscribe({
          next: (response) => {
            completedFiles++;
            
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
                  progress: Math.round((completedFiles / totalFiles) * 100),
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
                  progress: Math.round((completedFiles / totalFiles) * 100),
                  fileSuccess: false
                }
              });
            }
            
            // Continue with next file
            uploadNext(index + 1);
          },
          error: (error) => {
            completedFiles++;
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
                progress: Math.round((completedFiles / totalFiles) * 100),
                fileSuccess: false,
                error: error.error || error.message
              }
            });
            
            // Continue with next file even if this one failed
            uploadNext(index + 1);
          }
        });
      };

      // Start uploading from first file
      uploadNext(0);
    });
  }

  // uploadFolder is now handled by uploadFiles - kept for backward compatibility if needed
  uploadFolder(files: File[], subpath: string): Observable<{ type: 'progress' | 'complete' | 'error', data: any }> {
    return this.uploadFiles(files, subpath);
  }

}
