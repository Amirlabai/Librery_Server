import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {

  private notificationElement: HTMLDivElement | null = null;
  private timeoutId: any;
  private readonly DEFAULT_DURATION = 4000; 

  show(message: string, success: boolean = true, persistent: boolean = false, duration?: number) {
    
    // Clear any existing timeout FIRST
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }

    // Remove old notification if exists
    if (this.notificationElement) {
      this.notificationElement.remove();
      this.notificationElement = null;
    }

    // Create new notification
    const div = document.createElement('div');
    div.textContent = message;
    div.className = 'app-notification';  
    div.classList.add(success ? 'success' : 'error'); 

    document.body.appendChild(div);
    this.notificationElement = div;

    if (!persistent) {
      const autoDismissTime = duration || this.DEFAULT_DURATION;
      this.timeoutId = setTimeout(() => {
        this.clear();
      }, autoDismissTime);
    }
  }

  updateMessage(message: string) {
    if (this.notificationElement) {
      this.notificationElement.textContent = message;
    }
  }

  updateType(success: boolean) {
    if (this.notificationElement) {
      this.notificationElement.classList.remove('success', 'error');
      this.notificationElement.classList.add(success ? 'success' : 'error');
    }
  }

  clear(delay: number = 0) {
    
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }

    if (delay > 0) {
      this.timeoutId = setTimeout(() => {
        if (this.notificationElement) {
          this.notificationElement.remove();
          this.notificationElement = null;
        }
        this.timeoutId = null;
      }, delay);
    } else {
      if (this.notificationElement) {
        this.notificationElement.remove();
        this.notificationElement = null;
      }
    }
  }
}