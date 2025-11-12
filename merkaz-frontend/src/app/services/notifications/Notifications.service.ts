import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {

  private notificationElement: HTMLDivElement | null = null;
  private timeoutId: any;
  private readonly DEFAULT_DURATION = 4000; 

  show(message: string, success: boolean = true) {

    this.clear();

    const div = document.createElement('div');
    div.textContent = message;
    div.className = 'app-notification';  
    div.classList.add(success ? 'success' : 'error'); 

    document.body.appendChild(div);
    this.notificationElement = div;

    this.timeoutId = setTimeout(() => this.clear(), this.DEFAULT_DURATION);
  }

  clear() {
    if (this.notificationElement) {
      this.notificationElement.remove();
      this.notificationElement = null;
    }
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
  }
}
