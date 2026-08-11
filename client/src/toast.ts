type ToastType = 'success' | 'error' | 'info';

function createToast(message: string, type: ToastType): void {
  const containerId = 'toast-root';
  let root = document.getElementById(containerId);
  if (!root) {
    root = document.createElement('div');
    root.id = containerId;
    root.style.position = 'fixed';
    root.style.right = '16px';
    root.style.bottom = '16px';
    root.style.zIndex = '9999';
    root.style.display = 'flex';
    root.style.flexDirection = 'column';
    root.style.gap = '8px';
    document.body.appendChild(root);
  }

  const toast = document.createElement('div');
  toast.textContent = message;
  toast.style.padding = '10px 12px';
  toast.style.borderRadius = '10px';
  toast.style.color = '#111';
  toast.style.background = type === 'success' ? '#d1fae5' : type === 'error' ? '#fecaca' : '#e5e7eb';
  toast.style.boxShadow = '0 6px 18px rgba(0,0,0,0.12)';
  toast.style.maxWidth = '360px';
  toast.style.wordBreak = 'break-word';

  root.appendChild(toast);
  window.setTimeout(() => toast.remove(), 3500);
}

export function toastSuccess(message: string): void {
  createToast(message, 'success');
}

export function toastError(message: string): void {
  createToast(message, 'error');
}

export function toastInfo(message: string): void {
  createToast(message, 'info');
}

