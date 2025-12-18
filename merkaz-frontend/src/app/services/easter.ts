import { HttpClient } from "@angular/common/http";
import { HostListener, Injectable } from "@angular/core";
import { ApiConfigService } from "./api-config.service";


@Injectable({
    providedIn: 'root'
})
export class EasterService {

    private http: HttpClient;

    constructor(http: HttpClient,private apiConfig: ApiConfigService) {
        this.http = http;
    }
    private get baseUrl(): string {
        return this.apiConfig.getBackendUrl();
    }

    draw(){
        console.log('---');
        console.log('%c🐰🥚 Happy Easter! You\'ve found the Easter egg! 🥚🐰', 'color: #ff69b4; font-size: 16px;');
        console.log('In this developer console, you might find some hidden challenge!');
        console.log('Keep exploring and have fun!');
        console.log('-----------------------------------------------------------------------------');
        console.log('-----------------------------------------------------------------------------');
        console.log('-------------------------------------*---------------------------------------');
        console.log('--------------------------*----------------------*---------------------------');
        console.log('------------------*--------------------------------------*-------------------');
        console.log('-------------------------------------*---------------------------------------');
        console.log('-------------*----------------*------^-------*----------------*--------------');
        console.log('---------------------------------^\\--|--/^-----------------------------------');
        console.log('---------*-------------------------\\-|-/-------------------------*-----------');
        console.log('------------------------------------\\|/--------------------------------------');
        console.log('-------------------------------------|---------------------------------------');
        console.log('------------------------------------/|\\--------------------------------------');
        console.log('-----------------------------------/-|-\\-------------------------------------');
        console.log('----------------------------------/--|--\\------------------------------------');
        console.log('-----------------------------------------------------------------------------');
        console.log('-----------------------------------------------------------------------------');
        
    }
    sendEsterRequest() {
        this.http.get(`${this.baseUrl}/api/secret-clue`,{withCredentials:true}).subscribe({
            next: (res:any) =>{

            }
        }
            
        );
    }    
}