import { Component, DOCUMENT, HostListener, Inject, input } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { EasterService } from './services/easter';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from './services/auth.service';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { NotificationService } from './services/notifications/Notifications.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, MatIconModule,MatButtonModule,FormsModule,CommonModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent {
  protected title = 'merkaz-frontend';
  private pressedKeys: string = '';
  private readonly secretCode: string = '753951';
  public isActivated = false;
  public selectedPuzzleNum: number | null = null;
  public answerInput: string = '';
  public members: any[] = [];
  public challenges: any[] = [
  { name: 'puzzle1', solved: false },
  { name: 'puzzle2', solved: false },
  { name: 'puzzle3', solved: false },
  { name: 'puzzle4', solved: false },
  { name: 'puzzle5', solved: false },
  { name: 'puzzle6', solved: false },
  { name: 'puzzle7', solved: false },
  { name: 'puzzle8', solved: false },
  { name: 'puzzle9', solved: false },
  { name: 'puzzle10', solved: false }
];

  
  isDark = false;
  constructor(private easter:EasterService,
    @Inject(DOCUMENT) public document: Document,
    private http:HttpClient,
    private authService:AuthService,
    private notificationService:NotificationService) {
  }
  toggleMode() {
    this.isDark = !this.isDark;
    
    if (this.isDark) {
      this.document.body.classList.add('dark-mode');
    } else {
      this.document.body.classList.remove('dark-mode');
    }
  }

  ngOnInit() {
    this.initChallengeState();

    this.authService.onLogin().subscribe(() => {
      this.initChallengeState();
    });
  }
  private initChallengeState() {
    this.isActivated = false;
    this.members = [];
    this.challenges.forEach(c => c.solved = false);

    this.authService.refreshSession().subscribe({
      next: (userData: any) => {
        this.isActivated = userData.challenge === 'activated';
        if (this.isActivated) {
          this.loadGameData();
        }
      },
      error: () => {
        this.isActivated = false;
      }
    });
  }
  loadGameData() {
    this.http.get('http://localhost:8000/api/leaderboard-data', { withCredentials: true })
      .subscribe({
        next: (res: any) => {
          this.members = res.leaderboard;

          // נרמול פתרונות שהגיעו מהשרת
          const solved = res.user_solved.map((p: string) =>
            p.trim().toLowerCase()
          );

          this.challenges.forEach(ch => {
            ch.solved = solved.includes(ch.name.toLowerCase());
          });
        }
      });
  }
  activateCr() {
    if (this.isActivated) return;
    
    const body = {code:this.secretCode}

    this.http.post('http://localhost:8000/api/activate-challenge', body, { withCredentials: true })
    .subscribe({
      next: () => {
        this.isActivated = true;
        this.loadGameData();
      },
    });
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
      this.activateCr();
      this.pressedKeys = ''; 
    }
    
  }

  getPuzzle(puz: string) {  
    const fullPath = `http://localhost:8000/api/get-puzzle/${puz}`; 
    
    window.open(fullPath, '_blank');
  }
  submitAnswer() {
    if (!this.selectedPuzzleNum || !this.answerInput) return;

    const body = {
      puzzle_name: `puzzle${this.selectedPuzzleNum}`,
      answer: this.answerInput
    };

    this.http.post('http://localhost:8000/api/submit-answer', body, { withCredentials: true })
      .subscribe({
        next: (res: any) => {
          this.notificationService.show(res.message, true);
          this.answerInput = ''; 
          
          
          this.loadGameData(); 
        },
        error: (err) => {
          this.notificationService.show(err.error.message || 'Error occurred', false); 
        }
      });
  }

}




