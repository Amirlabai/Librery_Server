import { Component, OnInit} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

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
export class UploadFileComponent implements OnInit {


  subpath: string = '';
  selectedFiles: File[] = [];
  selectedFolderFiles: File[] = [];

  constructor(private http: HttpClient, private route: ActivatedRoute) {}

  ngOnInit() {
    // Get the current path from query parameters
    this.route.queryParams.subscribe(params => {
      if (params['path']) {
        this.subpath = params['path'];
      }
    });
  }

  onFileChange(event: any) {
    this.selectedFiles = Array.from(event.target.files);
  }

  onFolderChange(event: any) {
    this.selectedFolderFiles = Array.from(event.target.files);
  }

  onSubmitFiles() {
    const formData = new FormData();
    this.selectedFiles.forEach(file => formData.append('file', file));
    formData.append('subpath', this.subpath);

    this.http.post('http://localhost:8000/upload', formData, { withCredentials: true }).subscribe({
      next: (res: any) => {
        let message = '';
        if (res.message) {
          message = res.message;
        }
        
        // Display errors if any (even when some files succeeded)
        if (res.errors && res.errors.length > 0) {
          const errorMsg = res.errors.join('\n');
          if (message) {
            alert(message + '\n\nErrors:\n' + errorMsg);
          } else {
            alert('Some files failed to upload:\n\n' + errorMsg);
          }
        } else if (message) {
          alert(message);
        } else {
          alert('Files uploaded successfully');
        }
        
        window.location.reload();
      },
      error: (err: any) => {
        let errorMessage = 'Failed to upload files';
        
        if (err.error) {
          if (err.error.errors && err.error.errors.length > 0) {
            // Display all errors with file names
            errorMessage = 'Upload failed:\n\n' + err.error.errors.join('\n');
          } else if (err.error.error) {
            errorMessage = 'Upload failed: ' + err.error.error;
          }
        }
        
        alert(errorMessage);
        console.error(err);
      }
    });
  }

  onSubmitFolder() {
    const formData = new FormData();
    this.selectedFolderFiles.forEach(file => formData.append('file', file));
    formData.append('subpath', this.subpath);

    this.http.post('http://localhost:8000/upload', formData, { withCredentials: true }).subscribe({
      next: (res: any) => {
        let message = '';
        if (res.message) {
          message = res.message;
        }
        
        // Display errors if any (even when some files succeeded)
        if (res.errors && res.errors.length > 0) {
          let errorMsg = '';
          
          // Check if we have a summary format (when error_count > 5)
          if (res.error_count && res.error_count > 5) {
            // Display summary with file extensions
            errorMsg = res.errors.join('\n');
            if (res.error_count) {
              errorMsg = `Total: ${res.error_count} files failed\n\n${errorMsg}`;
            }
          } else {
            // Display individual file names (≤5 errors)
            errorMsg = res.errors.join('\n');
          }
          
          if (message) {
            alert(message + '\n\nFailed files:\n' + errorMsg);
          } else {
            alert('Some files failed to upload:\n\n' + errorMsg);
          }
        } else if (message) {
          alert(message);
        } else {
          alert('Folder uploaded successfully');
        }
        
        window.location.reload();
      },
      error: (err: any) => {
        let errorMessage = 'Failed to upload folder';
        
        if (err.error) {
          if (err.error.errors && err.error.errors.length > 0) {
            // Check if we have error_count (summary format)
            if (err.error.error_count && err.error.error_count > 5) {
              errorMessage = `Total: ${err.error.error_count} files failed\n\n` + err.error.errors.join('\n');
            } else {
              // Individual file names
              errorMessage = 'Upload failed:\n\n' + err.error.errors.join('\n');
            }
          } else if (err.error.error) {
            errorMessage = 'Upload failed: ' + err.error.error;
          }
        }
        
        alert(errorMessage);
        console.error(err);
      }
    });
  }
}
