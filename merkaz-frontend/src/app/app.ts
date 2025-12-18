import { Component, DOCUMENT, HostListener, Inject, input } from '@angular/core';
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
  private pressedKeys: string = '';
  private readonly secretCode: string = '753951';
  private readonly inputCode: string = '20202';

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
    this.easter.sendEsterRequest();
  }
  activateEasterEgg() {
      const puzzleUrl = 'assets/puzzle1.txt';
      window.location.href = puzzleUrl;
    
  }
  activeInput(){
    const inputUrl = 'assets/input1.txt';
    window.location.href = inputUrl;
  }

  @HostListener('document:keyup', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    
    if (event.key >= '0' && event.key <= '9') {
      this.pressedKeys += event.key;
    } else {
      this.pressedKeys = '';
      return;
    }

    if (this.pressedKeys.length > this.secretCode.length) {
      this.pressedKeys = this.pressedKeys.slice(-this.secretCode.length);
    }
    
    if (this.pressedKeys === this.secretCode) {
      this.activateEasterEgg();
      this.pressedKeys = ''; 
    }
    if(this.pressedKeys === this.inputCode){
      this.activeInput();
      this.pressedKeys = '';
    }
    
  }

 

}




