import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { ApiConfigService } from "./api-config.service";


@Injectable({
    providedIn: 'root'
})
export class ForgotPassService {
    
    constructor(
      private http: HttpClient,
      private apiConfig: ApiConfigService
    ) { }
    
    private get apiUrl(): string {
      return `${this.apiConfig.getBackendUrl()}/forgot-password`;
    }

    sendResetLink(email: string): Observable<any> {
        
        const payload = { email: email.trim() };
        return this.http.post(this.apiUrl, payload);
    }  

}