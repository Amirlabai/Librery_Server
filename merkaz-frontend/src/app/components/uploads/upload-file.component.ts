import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
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
export class UploadFileComponent {
  subpath: string = '';
  selectedFiles: File[] = [];
  selectedFolderFiles: File[] = [];

  constructor(private http: HttpClient) {}

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
    next: () => alert('Files uploaded'),
    error: err => console.error(err)
  });
}

  onSubmitFolder() {
    const formData = new FormData();
    this.selectedFolderFiles.forEach(file => formData.append('file', file));
    formData.append('subpath', this.subpath);

    this.http.post('/upload/folder', formData).subscribe({
      
      next: () => alert('Folder uploaded'),
      error: err => console.error(err)
    });
  }
}
