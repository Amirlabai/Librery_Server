import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ApiConfigService {
  private readonly BACKEND_URL_KEY = 'api_backend_url';
  
  /**
   * Get the backend API URL.
   * Checks localStorage first, then detects if running through ngrok or served from Flask,
   * otherwise defaults to localhost.
   */
  getBackendUrl(): string {
    // Check if user has manually set a backend URL
    const storedUrl = localStorage.getItem(this.BACKEND_URL_KEY);
    if (storedUrl) {
      return storedUrl;
    }
    
    // Detect environment
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      const port = window.location.port;
      
      // If accessed via ngrok, use relative URLs (Vite proxy handles it)
      if (hostname.includes('ngrok-free.dev') || 
          hostname.includes('ngrok-free.app') ||
          hostname.includes('ngrok.dev') ||
          hostname.includes('ngrok.app')) {
        return '';
      }
      
      // If served from Flask on port 8000, use relative URLs (same origin)
      if (port === '8000' || hostname === 'localhost' && port === '') {
        return '';
      }
    }
    
    // Default to localhost for local development (separate frontend/backend)
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

