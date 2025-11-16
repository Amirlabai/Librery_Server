import { Routes} from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { ForgotPasswordComponent } from './components/forgotpass/forgotpass.component';
import {DashboardComponent} from './components/dashborad/dashboard.component';
import { AdminUsersComponent } from './components/dashborad/admin-dash/users/admin-user.component';
import { AdminPendingComponent } from './components/dashborad/admin-dash/pending/admin-pending.component';
import { MetricsComponent } from './components/dashborad/admin-dash/metrics/metrics.component';
import { AdminUploadsComponent } from './components/dashborad/admin-dash/uploads/admin-uploads.component';
import { AdminDeniedComponent } from './components/dashborad/admin-dash/denied/admin-denied.component';
import { MyUploadsComponent } from './components/uploads/my-uploads.component';
import { UploadFileComponent } from './components/uploads/upload-file.component';
import { AuthGuard } from './services/auth.guard'; 
import { ResetPassComponent } from './components/resetpass/reset-pass.component';


export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password' , component:ResetPassComponent },

  // ------------------- DASHBOARD -------------------
  {
    path: 'dashboard',
    canActivate: [AuthGuard],
    children: [
      { path: '', component: DashboardComponent },
      { path: 'my-uploads', component: MyUploadsComponent },
      { path: 'upload', component: UploadFileComponent }
    ]
  },

  // ------------------- ADMIN -------------------
  { path: 'metrics', component: MetricsComponent, canActivate: [AuthGuard] },
  { path: 'users', component: AdminUsersComponent, canActivate: [AuthGuard] },
  { path: 'pending', component: AdminPendingComponent, canActivate: [AuthGuard] },
  { path: 'denied', component: AdminDeniedComponent, canActivate: [AuthGuard] },
  { path: 'uploads', component: AdminUploadsComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: 'login' }
];