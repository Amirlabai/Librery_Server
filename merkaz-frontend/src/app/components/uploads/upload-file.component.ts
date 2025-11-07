import { Component, OnInit} from '@angular/core';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UploadResponse, UserService } from '../../services/user.service';

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

  constructor(private userService:UserService, private route: ActivatedRoute) {}

  ngOnInit() {
    
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
    this.userService.uploadFiles(this.selectedFiles, this.subpath).subscribe({
      next: (res: UploadResponse) => {
        this.handleResponse(res, 'Files');
      },
      error: (err) => this.handleError(err, 'files')
    });
  }

  onSubmitFolder() {
    this.userService.uploadFolder(this.selectedFolderFiles, this.subpath).subscribe({
      next: (res: UploadResponse) => {
        this.handleResponse(res, 'Folder');
      },
      error: (err) => this.handleError(err, 'folder')
    });
  }

  private handleResponse(res: UploadResponse, type: 'Files' | 'Folder') {
    let message = res.message || `${type} uploaded successfully`;

    if (res.errors && res.errors.length > 0) {
      const errorMsg = res.errors.join('\n');
      if (res.error_count && res.error_count > 5) {
        alert(`${message}\n\nTotal: ${res.error_count} files failed\n\n${errorMsg}`);
      } else {
        alert(`${message}\n\nFailed items:\n${errorMsg}`);
      }
    } else {
      alert(message);
    }

    window.location.reload();
  }

  private handleError(err: any, type: string) {
    let errorMessage = `Failed to upload ${type}`;
    if (err.error) {
      if (err.error.errors?.length) {
        errorMessage = `Upload failed:\n\n${err.error.errors.join('\n')}`;
      } else if (err.error.error) {
        errorMessage = `Upload failed: ${err.error.error}`;
      }
    }
    alert(errorMessage);
    console.error(err);
  }
}
