import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const token = auth.getToken();

  let cloned = req.clone({
    withCredentials: true
  });

  if (token) {
    cloned = cloned.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return next(cloned).pipe(
    catchError(err => {
      // Only log out on actual authentication errors (401), not network errors
      // Network errors (status 0/undefined) can occur during large uploads and shouldn't cause logout
      if (err.status === 401) {
        auth.clearToken();
        sessionStorage.clear();
        router.navigate(['/login']);
      }
      return throwError(() => err);
    })
  );
};
