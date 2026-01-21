import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { UploadProgress, UploadProgressService } from '../../services/upload.service';

@Component({
  selector: 'app-global-upload-progress',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (progress.isActive) {
      <div class="upload-progress-float" [class.expanded]="isExpanded">
        <div class="progress-header" (click)="toggleExpand()">
          <div class="header-left">
            <span class="upload-icon">
              @if (progress.type === 'file') {
                📁
              } @else {
                📂
              }
            </span>
            <div class="header-info">
              <span class="status-text">Uploading...</span>
              <span class="progress-text">{{ progress.uploadedCount }} / {{ progress.totalCount }}</span>
            </div>
          </div>
          <div class="header-right">
            <span class="progress-percent">{{ progress.progress }}%</span>
            <button class="expand-btn" type="button">
              @if (isExpanded) {
                ▼
              } @else {
                ▲
              }
            </button>
          </div>
        </div>

        <div class="progress-track">
          <div class="progress-fill" [style.width.%]="progress.progress"></div>
        </div>

        @if (isExpanded) {
          <div class="progress-details">
            @if (progress.currentFile) {
              <div class="detail-row">
                <span class="detail-label">Current:</span>
                <span class="detail-value file-name">{{ progress.currentFile }}</span>
              </div>
            }
            
            <div class="detail-stats">
              @if (progress.speed) {
                <div class="stat-item">
                  <span class="stat-label">Speed</span>
                  <span class="stat-value">{{ progress.speed }}</span>
                </div>
              }
              @if (progress.timeRemaining) {
                <div class="stat-item">
                  <span class="stat-label">Time Left</span>
                  <span class="stat-value">{{ progress.timeRemaining }}</span>
                </div>
              }
            </div>

            <button class="view-details-btn" type="button" (click)="navigateToUpload()">
              View Details →
            </button>
          </div>
        }
      </div>
    }
  `,
  styles: [`
    .upload-progress-float {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 360px;
      background: var(--card-bg);
      border-radius: 12px;
      box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.12),
        0 4px 16px rgba(0, 0, 0, 0.08);
      border: 1px solid var(--table-border-color);
      z-index: 999;
      overflow: hidden;
      transition: all 0.3s ease;
      animation: slideIn 0.3s ease;
    }

    @keyframes slideIn {
      from {
        transform: translateY(100px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }

    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px;
      cursor: pointer;
      user-select: none;
      transition: background-color 0.2s ease;
    }

    .progress-header:hover {
      background-color: var(--buttons-color);
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
      min-width: 0;
    }

    .upload-icon {
      font-size: 24px;
      flex-shrink: 0;
    }

    .header-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }

    .status-text {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-color);
    }

    .progress-text {
      font-size: 12px;
      color: var(--placeholder-color);
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }

    .progress-percent {
      font-size: 16px;
      font-weight: 700;
      color: var(--primary-buttons);
    }

    .expand-btn {
      background: transparent;
      border: none;
      color: var(--placeholder-color);
      font-size: 14px;
      cursor: pointer;
      padding: 4px 8px;
      transition: color 0.2s ease;
    }

    .expand-btn:hover {
      color: var(--primary-buttons);
    }

    .progress-track {
      height: 6px;
      background-color: var(--buttons-color);
      position: relative;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary-buttons), #4285f4);
      transition: width 0.3s ease;
      box-shadow: 0 0 10px rgba(26, 115, 232, 0.3);
    }

    .progress-details {
      padding: 16px;
      border-top: 1px solid var(--table-border-color);
      animation: expandDetails 0.3s ease;
    }

    @keyframes expandDetails {
      from {
        opacity: 0;
        max-height: 0;
      }
      to {
        opacity: 1;
        max-height: 200px;
      }
    }

    .detail-row {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
    }

    .detail-label {
      font-size: 12px;
      font-weight: 600;
      color: var(--placeholder-color);
      flex-shrink: 0;
    }

    .detail-value {
      font-size: 12px;
      color: var(--text-color);
    }

    .file-name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .detail-stats {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-bottom: 12px;
    }

    .stat-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 8px;
      background-color: var(--buttons-color);
      border-radius: 6px;
    }

    .stat-label {
      font-size: 10px;
      font-weight: 600;
      color: var(--placeholder-color);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .stat-value {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-color);
    }

    .view-details-btn {
      width: 100%;
      padding: 10px;
      background: var(--primary-buttons);
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .view-details-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3);
    }

    .view-details-btn:active {
      transform: translateY(0);
    }

    /* Mobile Responsive */
    @media (max-width: 768px) {
      .upload-progress-float {
        width: calc(100vw - 32px);
        right: 16px;
        bottom: 80px;
      }
    }

    @media (max-width: 480px) {
      .upload-progress-float {
        width: calc(100vw - 24px);
        right: 12px;
        bottom: 70px;
      }

      .progress-header {
        padding: 12px;
      }

      .upload-icon {
        font-size: 20px;
      }

      .status-text {
        font-size: 13px;
      }

      .progress-text {
        font-size: 11px;
      }

      .progress-percent {
        font-size: 14px;
      }
    }
  `]
})
export class GlobalUploadProgressComponent implements OnInit, OnDestroy {

  progress: UploadProgress = {
    isActive: false,
    type: 'file',
    progress: 0,
    uploadedCount: 0,
    totalCount: 0,
    currentFile: '',
    speed: '',
    timeRemaining: ''
  };

  isExpanded = false;
  private subscription?: Subscription;

  constructor(
    private uploadProgressService: UploadProgressService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Subscribe to progress updates
    this.subscription = this.uploadProgressService.progress$.subscribe(
      progress => {
        this.progress = progress;
        
        // Auto-expand when upload starts
        if (progress.isActive && progress.progress === 0) {
          this.isExpanded = true;
        }
        
        // Auto-collapse when upload completes
        if (progress.progress === 100) {
          setTimeout(() => {
            this.isExpanded = false;
          }, 1000);
        }
      }
    );
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }

  toggleExpand(): void {
    this.isExpanded = !this.isExpanded;
  }

  navigateToUpload(): void {
    this.router.navigate(['/upload-content']);
  }
}