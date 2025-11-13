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
  isUploadingFile: boolean = false;
  isUploadingFolder: boolean = false;


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
    this.isUploadingFile = true;

    this.userService.uploadFiles(this.selectedFiles, this.subpath).subscribe({

      next: () => {

        
        this.isUploadingFile = false;

        setTimeout(() => {

          this.notificationService.show('Files uploaded successfully', true);

          setTimeout(() => {
            window.location.reload();
          }, 2000);

        }); 
      },

      error: () => {
        this.isUploadingFile = false;
        this.notificationService.show('Failed to upload files', false);
      }
    });
  }

  onSubmitFolder() {

    this.isUploadingFolder = true;

    this.userService.uploadFiles(this.selectedFiles, this.subpath).subscribe({

      next: () => {

        
        this.isUploadingFolder = false;

        setTimeout(() => {

          this.notificationService.show('Folders uploaded successfully',true);

          setTimeout(() => {
            window.location.reload();
          }, 2000);

        }); 
      },

      error: () => {
        this.isUploadingFolder = false;
        this.notificationService.show('Failed to upload folder',false);
      }
    });
  }
}