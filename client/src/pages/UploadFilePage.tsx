import React, { useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import './dashboard.css';
import { toastError, toastSuccess } from '../toast';
import { uploadFiles } from '../api';
import { useUploadProgress } from '../uploadProgress';

function formatBytes(bytes: number): string {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${Math.round((bytes / k ** i) * 10) / 10} ${sizes[i]}`;
}

export default function UploadFilePage() {
  const [searchParams] = useSearchParams();
  const uploadPath = searchParams.get('path') || '';
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const { startUpload, updateProgress, completeUpload } = useUploadProgress();

  const fileCount = useMemo(() => selectedFiles.length, [selectedFiles]);

  function addFiles(list: FileList | File[]) {
    const next = Array.from(list);
    setSelectedFiles((prev) => {
      const names = new Set(prev.map((f) => `${f.name}:${f.size}`));
      const merged = [...prev];
      for (const file of next) {
        const key = `${file.name}:${file.size}`;
        if (!names.has(key)) merged.push(file);
      }
      return merged;
    });
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy || fileCount === 0) return;
    setBusy(true);

    try {
      startUpload('file', fileCount);
      const res = await uploadFiles(selectedFiles, uploadPath, (event) => {
        updateProgress({
          isActive: event.isUploading,
          type: 'file',
          progress: event.progress,
          uploadedCount: event.successfulFiles + event.failedFiles,
          totalCount: event.totalFiles,
          currentFile: event.currentFile,
        });
      });

      if (res.successful.length > 0) toastSuccess(`Uploaded ${res.successful.length} file(s)`);
      if (res.failed.length > 0) toastError(`${res.failed.length} file(s) failed`);
      completeUpload();
      setSelectedFiles([]);
      if (inputRef.current) inputRef.current.value = '';
    } catch (err: any) {
      toastError(err?.message || 'Upload failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-root">
      <div className="container upload-page-container">
        <header className="header">
          <h1>Upload files</h1>
          <Link to="/dashboard" className="my-uploads-btn">
            Back to files
          </Link>
        </header>

        {uploadPath ? (
          <p className="path-bar">
            Destination: <span className="pathFolders">{uploadPath}</span>
          </p>
        ) : (
          <p className="path-bar">Destination: home folder</p>
        )}

        <form onSubmit={onSubmit} className="upload-form">
          <input
            ref={inputRef}
            id="fileInput"
            type="file"
            multiple
            className="upload-input"
            onChange={(e) => {
              if (e.target.files) addFiles(e.target.files);
            }}
          />

          <div
            className={`upload-dropzone${dragging ? ' is-dragging' : ''}`}
            role="button"
            tabIndex={0}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                inputRef.current?.click();
              }
            }}
            onDragEnter={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              setDragging(false);
            }}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
            }}
          >
            <p className="upload-dropzone__title">Drop files here</p>
            <p className="upload-dropzone__hint">or click to browse from your computer</p>
          </div>

          {fileCount > 0 && (
            <ul className="upload-file-list">
              {selectedFiles.map((file) => (
                <li key={`${file.name}-${file.size}-${file.lastModified}`}>
                  <span className="upload-file-name">{file.name}</span>
                  <span className="upload-file-size">{formatBytes(file.size)}</span>
                </li>
              ))}
            </ul>
          )}

          <p className="upload-meta">{fileCount} file(s) selected</p>

          <button disabled={busy || fileCount === 0} type="submit" className="upload-btn upload-submit">
            {busy ? 'Uploading...' : 'Upload'}
          </button>
        </form>
      </div>
    </div>
  );
}
