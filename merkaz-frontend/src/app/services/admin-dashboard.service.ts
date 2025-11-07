import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";

export interface DeniedUser {
  email: string;
}
export interface PendingUser {
  email: string;
  status: string;
}
export interface UploadItem {
  timestamp: string;
  email: string;
  filename: string;
  path: string;
}

@Injectable({
  providedIn: 'root'
})

export class AdminDashboardService {

  private baseUrl = 'http://localhost:8000/admin';

  constructor(private http: HttpClient) {}

  loadDeniedUsers(): Observable<DeniedUser[]> {
    return this.http.get<DeniedUser[]>(`${this.baseUrl}/denied`, { withCredentials: true });
  }

  moveToPending(email: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/re-pend/${email}`, {}, { withCredentials: true });
  }

  downloadLog(type: string): void {
    const url = `${this.baseUrl}/metrics/download/${type}`;
    window.open(url, '_blank');
  }
  
  loadPendingUsers(): Observable<PendingUser[]> {
    return this.http.get<PendingUser[]>(
      `${this.baseUrl}/pending`,
      { withCredentials: true }
    );
  }

  approveUser(email: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/approve/${email}`, {}, { withCredentials: true });
  }

  denyUser(email: string): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/deny/${email}`,
      {},
      { withCredentials: true }
    );
  }

  loadUploads(): Observable<UploadItem[]> {
    return this.http.get<UploadItem[]>(
      `${this.baseUrl}/uploads`,
      { withCredentials: true }
    );
  }

  approveUpload(filename: string, targetPath: string): Observable<any> {
    const payload = { target_path: targetPath };
    return this.http.post(
      `${this.baseUrl}/move_upload/${filename}`,
      payload,
      { withCredentials: true }
    );
  }

  declineUpload(filename: string, targetPath: string): Observable<any> {
    const payload = { target_path: targetPath };
    return this.http.post(
      `${this.baseUrl}//decline_upload/${filename}`,
      payload,
      { withCredentials: true }
    );
  }

  loadUsers(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/users`, { withCredentials: true });
  }
  
  toggleRole(email: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/toggle-role/${email}`, {}, { withCredentials: true });
  }

  toggleStatus(email: string) : Observable<any> {
    return this.http.post('${this.baseUrl}/toggle-status/${email}', {}, { withCredentials: true });
  }
  
  startHeartbeat(): void {

    setInterval(() => {
      this.http.post(`${this.baseUrl}/heartbeat`, {}, { withCredentials: true })
        .subscribe({
          next: res => console.log('✅ Heartbeat OK', res),
          error: err => console.error('❌ Heartbeat failed', err)
        });
    }, 900000); 
  }
}