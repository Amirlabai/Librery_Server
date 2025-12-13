import { Component, DOCUMENT, Inject } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { EasterService } from './services/easter';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, MatIconModule,MatButtonModule,],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent {
  protected title = 'merkaz-frontend';

  isDark = false;
  constructor(private easter:EasterService,@Inject(DOCUMENT) public document: Document) {
  }
  toggleMode() {
    this.isDark = !this.isDark;
    
    if (this.isDark) {
      this.document.body.classList.add('dark-mode');
    } else {
      this.document.body.classList.remove('dark-mode');
    }
  }

  ngOnInit(){
    
    this.easter.draw();
  }

}


