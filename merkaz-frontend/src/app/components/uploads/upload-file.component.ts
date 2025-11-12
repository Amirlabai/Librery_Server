import { Component, OnInit} from '@angular/core';
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
export class UploadFileComponent implements OnInit {


  subpath: string = '';
  selectedFiles: File[] = [];
  selectedFolderFiles: File[] = [];


  constructor(private userService:UserService, private route: ActivatedRoute,private notificationService:NotificationService) {}

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
      next: () => {
        this.notificationService.show('Files uploaded successfully',true);
        setTimeout(() => {
            window.location.reload();
          }, 4000);
        },
      error: () => {
        this.notificationService.show('Failed to upload files',false);
      } 
    });
  }

  onSubmitFolder() {
    this.userService.uploadFolder(this.selectedFolderFiles, this.subpath).subscribe({
      next: () => {

        this.notificationService.show('Folders uploaded successfully',true);

        setTimeout(() => {
          window.location.reload();
        }, 4000);
      },
      error: () => {
        this.notificationService.show('Failed to upload folder',false);
      }
    });
  }

}
