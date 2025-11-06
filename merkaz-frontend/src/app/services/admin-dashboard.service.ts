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
    const url = `${this.baseUrl}/admin/metrics/download/${type}`;
    window.open(url, '_blank');
  }
  
  loadPendingUsers(): Observable<PendingUser[]> {
    return this.http.get<PendingUser[]>(
      `${this.baseUrl}/admin/pending`,
      { withCredentials: true }
    );
  }

  approveUser(email: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/approve/${email}`, {}, { withCredentials: true });
  }

  denyUser(email: string): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/admin/deny/${email}`,
      {},
      { withCredentials: true }
    );
  }
}