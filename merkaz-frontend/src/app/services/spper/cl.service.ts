import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { ApiConfigService } from "../api-config.service";

@Injectable({ providedIn: 'root' })
export class ChallengeService {

  public challenges: any[] = [
        { name: 'puzzle1', solved: false },
        { name: 'puzzle2', solved: false },
        { name: 'puzzle3', solved: false },
        { name: 'puzzle4', solved: false },
        { name: 'puzzle5', solved: false },
    ];

  constructor(
  private http: HttpClient,
  private apiConfig: ApiConfigService
) {}

  private get baseUrl(): string {
    return this.apiConfig.getBackendUrl();
  }
  loadLeaderboard() {
    return this.http.get<any>(
      `${this.baseUrl}/api/leaderboard-data`,
      { withCredentials: true }
    );
  }

  submitAnswer(puzzleNum: number, answer: string) {
    return this.http.post<any>(
      `${this.baseUrl}/api/submit-answer`,
      {
        puzzle_name: `puzzle${puzzleNum}`,
        answer
      },
      { withCredentials: true }
    );
  }

  syncSolved(userSolved: string[]) {
    const solved = userSolved.map(s => s.trim().toLowerCase());
    this.challenges.forEach(c =>
      c.solved = solved.includes(c.name)
    );
  }
}