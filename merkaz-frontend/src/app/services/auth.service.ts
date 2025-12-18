import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { ApiConfigService } from './api-config.service';


export interface LoginResponse {
  token?: string;
  role?: string;
  message?: string;
  error?: string;
}

export interface RegisterResponse {
  message?: string;
  error?: string;
}

@Injectable({ providedIn: 'root' })

export class AuthService {
  private readonly tokenKey = 'token';
  private loginState$ = new Subject<void>();

  constructor(
    private http: HttpClient,
    private apiConfig: ApiConfigService
  ) {}
  
  private get baseUrl(): string {
    return this.apiConfig.getBackendUrl();
  }

  login(email: string, password: string): Observable<LoginResponse> {
    const payload = { email: email.trim(), password: password.trim() };
    return this.http.post<LoginResponse>(`${this.baseUrl}/login`, payload, { withCredentials: true });
  }

  register(first_name:string,last_name:string,email: string, password: string): Observable<RegisterResponse> {
    const payload = {first_name,last_name, email: email.trim(), password: password.trim() };
    return this.http.post<RegisterResponse>(`${this.baseUrl}/register`, payload);
  }
  resetPass(token: string, password: string) {
    return this.http.post(
      `${this.baseUrl}/reset-password/${token}`,
      { password }
    );
  }

  saveToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }


  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  clearToken(): void {
    localStorage.removeItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }
  refreshSession(): Observable<any> {
    return this.http.get(`${this.baseUrl}/refresh-session`, { withCredentials: true });
  }
  notifyLogin() {
    this.loginState$.next();
  }

  onLogin() {
    return this.loginState$.asObservable();
  }
}
