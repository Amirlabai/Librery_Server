import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {

  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): Observable<boolean> {
    return this.auth.refreshSession().pipe(
      tap((res: { token?: string }) => {
        if (res?.token) {
          this.auth.saveToken(res.token);
        }
      }),
      map(() => true),
      catchError(() => {
        this.auth.clearToken();
        localStorage.removeItem('role');
        localStorage.removeItem('email');
        localStorage.removeItem('fullName');
        sessionStorage.clear();
        this.router.navigate(['/login']);
        return of(false);
      })
    );
  }
}
