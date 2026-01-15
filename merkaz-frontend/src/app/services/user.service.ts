import { HttpClient, HttpEvent, HttpEventType, HttpRequest } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";
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

  uploadFiles(files: File[], subpath: string): Observable<number | any> {
    const formData = new FormData();
    files.forEach(file => formData.append('file', file));
    formData.append('subpath', subpath);

    // Create request with progress tracking enabled
    const req = new HttpRequest('POST', `${this.baseUrl}/upload`, formData, {
      reportProgress: true,
      withCredentials: true
    });

    // Transform HTTP events into progress percentages or response
    return this.http.request(req).pipe(
      map((event: HttpEvent<any>) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            // Calculate and return upload percentage
            if (event.total) {
              const percentDone = Math.round((100 * event.loaded) / event.total);
              return percentDone;
            }
            return 0;

          case HttpEventType.Response:
            // Upload complete, return the response body
            return event.body;

          default:
            return 0;
        }
      })
    );
  }

  uploadFolder(files: File[], subpath: string): Observable<number | any> {
    const formData = new FormData();
    files.forEach(file => formData.append('file', file));
    formData.append('subpath', subpath);

    // Create request with progress tracking enabled
    const req = new HttpRequest('POST', `${this.baseUrl}/upload`, formData, {
      reportProgress: true,
      withCredentials: true
    });

    // Transform HTTP events into progress percentages or response
    return this.http.request(req).pipe(
      map((event: HttpEvent<any>) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            // Calculate and return upload percentage
            if (event.total) {
              const percentDone = Math.round((100 * event.loaded) / event.total);
              return percentDone;
            }
            return 0;

          case HttpEventType.Response:
            // Upload complete, return the response body
            return event.body;

          default:
            return 0;
        }
      })
    );
  }

}