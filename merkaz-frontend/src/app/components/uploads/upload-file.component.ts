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
        if (res.message) {
          alert(res.message);
        } else {
          alert('Files uploaded successfully');
        }
        window.location.reload();
      },
      error: (err: any) => {
        if (err.error && err.error.error) {
          alert('Error: ' + err.error.error);
        } else if (err.error && err.error.errors) {
          alert('Errors: ' + err.error.errors.join(', '));
        } else {
          alert('Failed to upload files');
        }
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
        if (res.message) {
          alert(res.message);
        } else {
          alert('Folder uploaded successfully');
        }
        window.location.reload();
      },
      error: (err: any) => {
        if (err.error && err.error.error) {
          alert('Error: ' + err.error.error);
        } else {
          alert('Failed to upload folder');
        }
        console.error(err);
      }
    });
  }
}
