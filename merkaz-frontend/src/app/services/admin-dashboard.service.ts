import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";

export interface DeniedUser {
  email: string;
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
    return this.http.post(`${this.baseUrl}/admin/re-pend/${email}`, {}, { withCredentials: true });
  }
}