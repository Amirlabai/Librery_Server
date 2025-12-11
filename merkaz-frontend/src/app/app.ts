import { Component } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { EasterService } from './services/easter';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, MatIconModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent {
  protected title = 'merkaz-frontend';


  constructor(private easter:EasterService) {
  }

  ngOnInit(){
    
    this.easter.draw();
  }

}


