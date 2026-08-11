import React, { createContext, useContext, useMemo, useState } from 'react';

export type UploadProgressType = 'file' | 'folder';

export interface UploadProgress {
  isActive: boolean;
  type: UploadProgressType;
  progress: number; // 0..100
  uploadedCount: number;
  totalCount: number;
  currentFile: string;
  speed: string;
  timeRemaining: string;
}

interface UploadProgressContextValue {
  progress: UploadProgress;
  startUpload: (type: UploadProgressType, totalCount: number) => void;
  updateProgress: (partial: Partial<UploadProgress>) => void;
  completeUpload: () => void;
  cancelUpload: () => void;
}

const UploadProgressContext = createContext<UploadProgressContextValue | null>(null);

const initialProgress: UploadProgress = {
  isActive: false,
  type: 'file',
  progress: 0,
  uploadedCount: 0,
  totalCount: 0,
  currentFile: '',
  speed: '',
  timeRemaining: '',
};

export function UploadProgressProvider({ children }: { children: React.ReactNode }) {
  const [progress, setProgress] = useState<UploadProgress>(initialProgress);

  const value = useMemo<UploadProgressContextValue>(() => {
    return {
      progress,
      startUpload: (type, totalCount) => {
        setProgress({
          isActive: true,
          type,
          progress: 0,
          uploadedCount: 0,
          totalCount,
          currentFile: '',
          speed: '',
          timeRemaining: '',
        });
      },
      updateProgress: (partial) => {
        setProgress((current) => ({
          ...current,
          ...partial,
        }));
      },
      completeUpload: () => {
        setProgress((current) => ({
          ...current,
          isActive: false,
          progress: 100,
        }));
        window.setTimeout(() => {
          setProgress(initialProgress);
        }, 2000);
      },
      cancelUpload: () => setProgress(initialProgress),
    };
  }, [progress]);

  return <UploadProgressContext.Provider value={value}>{children}</UploadProgressContext.Provider>;
}

export function useUploadProgress(): UploadProgressContextValue {
  const ctx = useContext(UploadProgressContext);
  if (!ctx) throw new Error('useUploadProgress must be used within UploadProgressProvider');
  return ctx;
}

