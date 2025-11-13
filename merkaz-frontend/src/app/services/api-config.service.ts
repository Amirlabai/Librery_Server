import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ApiConfigService {
  private readonly BACKEND_URL_KEY = 'api_backend_url';
  
  /**
   * Get the backend API URL.
   * Checks localStorage first, then detects if running through ngrok,
   * otherwise defaults to localhost.
   */
  getBackendUrl(): string {
    // Check if user has manually set a backend URL
    const storedUrl = localStorage.getItem(this.BACKEND_URL_KEY);
    if (storedUrl) {
      return storedUrl;
    }
    
    // Detect if frontend is accessed through ngrok
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      const protocol = window.location.protocol;
      
      // If accessed via ngrok, we need to use the backend ngrok URL
      // Since ngrok creates different URLs for frontend and backend,
      // we'll need to prompt or use a pattern
      if (hostname.includes('ngrok-free.dev') || 
          hostname.includes('ngrok-free.app') ||
          hostname.includes('ngrok.dev') ||
          hostname.includes('ngrok.app')) {
        // For ngrok, you'll need to set the backend URL manually
        // This is a placeholder - user should set it via setBackendUrl()
        // For now, return localhost (won't work externally)
        return 'http://localhost:8000';
      }
    }
    
    // Default to localhost for local development
    return 'http://localhost:8000';
  }
  
  /**
   * Set a custom backend URL (useful for ngrok)
   */
  setBackendUrl(url: string): void {
    localStorage.setItem(this.BACKEND_URL_KEY, url);
  }
  
  /**
   * Clear the custom backend URL and use defaults
   */
  clearBackendUrl(): void {
    localStorage.removeItem(this.BACKEND_URL_KEY);
  }
}

