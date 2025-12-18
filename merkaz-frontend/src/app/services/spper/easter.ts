import { HttpClient } from "@angular/common/http";
import { ApiConfigService } from "../api-config.service";
import { Injectable } from "@angular/core";


@Injectable({
    providedIn: 'root'
})
export class EasterService {

    private buffer = '';
    private readonly secret = '753951';
    private http: HttpClient;

    constructor(http: HttpClient,private apiConfig: ApiConfigService) {
        this.http = http;
    }
    private get baseUrl(): string {
        return this.apiConfig.getBackendUrl();
    }

    handleKey(key: string, onMatch: () => void) {
        if (key < '0' || key > '9') {
        this.buffer = '';
        return;
        }

        this.buffer += key;
        this.buffer = this.buffer.slice(-this.secret.length);

        if (this.buffer === this.secret) {
        this.buffer = '';
        onMatch();
        }
    }
    activate() {
        return this.http.post(
        `${this.apiConfig.getBackendUrl()}/api/activate-challenge`,
        { code: this.secret },
        { withCredentials: true }
        );
    }
    draw(){
        console.log('---');
        console.log('%c🐰🥚 Happy Easter! You\'ve found the Easter egg! 🥚🐰', 'color: #ff69b4; font-size: 16px;');
        console.log('In this developer console, you might find some hidden challenge!');
        console.log('Keep exploring and have fun!');
     //   console.log('-----------------------------------------------------------------------------');
     //   console.log('-----------------------------------------------------------------------------');
     //   console.log('-------------------------------------*---------------------------------------');
     //   console.log('--------------------------*----------------------*---------------------------');
      //  console.log('------------------*--------------------------------------*-------------------');
      //  console.log('-------------------------------------*---------------------------------------');
        //console.log('-------------*----------------*------^-------*----------------*--------------');
       // console.log('---------------------------------^\\--|--/^-----------------------------------');
        //console.log('---------*-------------------------\\-|-/-------------------------*-----------');
        //console.log('------------------------------------\\|/--------------------------------------');
        //console.log('-------------------------------------|---------------------------------------');
        //console.log('------------------------------------/|\\--------------------------------------');
        //console.log('-----------------------------------/-|-\\-------------------------------------');
        //console.log('----------------------------------/--|--\\------------------------------------');
        //console.log('-----------------------------------------------------------------------------');
        //console.log('-----------------------------------------------------------------------------');
        
    }
    sendEsterRequest() {
        this.http.get(`${this.baseUrl}/api/secret-clue`,{withCredentials:true}).subscribe({
            next: (res:any) =>{

            }
        }
            
        );
    }    
}