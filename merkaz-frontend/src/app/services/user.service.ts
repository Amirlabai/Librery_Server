import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
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

  uploadFiles(files: File[], subpath: string): Observable<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('file', file));
    formData.append('subpath', subpath);

    return this.http.post<any>(`${this.baseUrl}/upload`, formData, { withCredentials: true });
  }

  uploadFolder(files: File[], subpath: string): Observable<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('file', file));
    formData.append('subpath', subpath);

    return this.http.post<any>(`${this.baseUrl}/upload`, formData, { withCredentials: true });
  }

}  