import { HttpClient } from "@angular/common/http";
import { HostListener, Injectable } from "@angular/core";


@Injectable({
    providedIn: 'root'
})
export class EasterService {

    private http: HttpClient;

    constructor(http: HttpClient) {
        this.http = http;
    }

    draw(){
        console.log('---');
        console.log('%c🐰🥚 Happy Easter! You\'ve found the Easter egg! 🥚🐰', 'color: #ff69b4; font-size: 16px;');
        console.log('In this developer console, you might find some hidden surprises!');
        console.log('There are 4 more Easter eggs hidden throughout the application. Keep exploring and have fun!');
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
        this.http.get('https://nagoamir-server.onrender.com/api/easter-egg')
            .subscribe();
    }
    
}