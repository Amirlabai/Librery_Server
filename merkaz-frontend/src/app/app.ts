import { Component, DOCUMENT, HostListener, Inject, input } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { EasterService } from './services/spper/easter';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from './services/auth.service';
import { FormsModule } from '@angular/forms';
import { NotificationService } from './services/notifications/Notifications.service';
import { CommonModule } from '@angular/common';
import { ChallengeService } from './services/spper/cl.service';
import { ApiConfigService } from './services/api-config.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, MatIconModule,MatButtonModule,FormsModule,CommonModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent {
  protected title = 'merkaz-frontend';
  isDark = false;
  isActivated = false;
  members: any[] = [];
  selectedPuzzleNum: number | 0 = 0;
  answerInput = '';
  isHideChall = false;
  isDeviceSupported = true;
  

  
  constructor(
    @Inject(DOCUMENT) private doc: Document,
    private auth: AuthService,
    private cl: ChallengeService,
    private easter: EasterService,
    private notify: NotificationService,
    private apiConfig: ApiConfigService
  ) {}
  toggleMode() {
    this.isDark = !this.isDark;
    
    if (this.isDark) {
      this.doc.body.classList.add('dark-mode');
    } else {
      this.doc.body.classList.remove('dark-mode');
    }
  }

  ngOnInit() {

    this.isDeviceSupported = !this.isMobile();

    if (!this.isDeviceSupported) {
      return; 
    }

    this.auth.onLogin().subscribe(() => this.init());
    this.easter.sendEsterRequest();
    this.init();
  }

  private init() {

    if (!this.isDeviceSupported) {
      return;
    }

    this.auth.refreshSession().subscribe({
      next: user => {
        this.isActivated = user.challenge === 'activated';
        if (this.isActivated) {
          this.loadGame();
        }
      },
      error: () => {
        this.isActivated = false;
      }
    });
  }
  loadGame() {
    this.cl.loadLeaderboard().subscribe(res => {
      this.members = res.leaderboard;
      this.cl.syncSolved(res.user_solved);
    });
  }
  submitAnswer(puzzleNum: number, answer: string) {
    this.cl.submitAnswer(puzzleNum, answer).subscribe({
      next: res => {
        this.notify.show(res.message, true);
        if(res.message.startsWith('Correct')) {
          this.answerInput = '';
          this.selectedPuzzleNum = 0;
        }
        this.loadGame();
      },
      error: err => {
        this.notify.show(err.error.message, false);
      }
    });
  }
  @HostListener('document:keyup', ['$event'])
  onKey(e: KeyboardEvent) {
    this.easter.handleKey(e.key, () => {
      this.easter.activate().subscribe(() => this.loadGame());
    });
  }

  getPuzzle(puz: string) {
    // Validate input
    if (!puz || typeof puz !== 'string' || puz.trim().length === 0) {
      this.notify.show('Invalid puzzle name', false);
      return;
    }

    try {
      // Use ApiConfigService to get the correct backend URL (works in all environments)
      const baseUrl = this.apiConfig.getBackendUrl();
      // URL encode the puzzle name to handle special characters
      const encodedPuz = encodeURIComponent(puz.trim());
      const fullPath = `${baseUrl}/api/get-puzzle/${encodedPuz}`;
      
      // Attempt to open the puzzle in a new window
      const newWindow = window.open(fullPath, '_blank');
      
      // Check if popup was blocked
      if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
        this.notify.show('Popup blocked. Please allow popups for this site.', false);
      }
    } catch (error) {
      console.error('Error opening puzzle:', error);
      this.notify.show('Failed to open puzzle. Please try again.', false);
    }
  }
  get challenges() {
    return this.cl.challenges;
  }
  toggleChallenge(){
    this.isHideChall = !this.isHideChall;
  }
  isMobile(): boolean {
    return /android|iphone|ipad|mobile/i.test(navigator.userAgent);
  }
  
}




