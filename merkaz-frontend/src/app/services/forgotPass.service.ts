import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";


@Injectable({
    providedIn: 'root'
})
export class ForgotPassService {
    
    private apiUrl = 'http://localhost:8000/forgot-password';

    constructor(private http:HttpClient) { }

    sendResetLink(email: string): Observable<any> {
        
        const payload = { email: email.trim() };
        return this.http.post(this.apiUrl, payload);
    }  

}