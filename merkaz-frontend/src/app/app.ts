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
  

  
  constructor(
    @Inject(DOCUMENT) private doc: Document,
    private auth: AuthService,
    private cl: ChallengeService,
    private easter: EasterService,
    private notify: NotificationService
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
    this.auth.onLogin().subscribe(() => this.init());
    this.easter.sendEsterRequest();
    this.init();
  }
  private init() {
    this.auth.refreshSession().subscribe(user => {
      this.isActivated = user.challenge === 'activated';
      if (this.isActivated) {
        this.loadGame();
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
    const fullPath = `http://localhost:8000/api/get-puzzle/${puz}`; 
    
    window.open(fullPath, '_blank');
  }
  get challenges() {
    return this.cl.challenges;
  }
  toggleChallenge(){
    this.isHideChall = !this.isHideChall;
  }
  
}




