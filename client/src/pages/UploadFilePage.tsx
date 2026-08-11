import React, { useMemo, useState } from 'react';
import { toastError, toastSuccess } from '../toast';
import { uploadFiles } from '../api';
import { useUploadProgress } from '../uploadProgress';

export default function UploadFilePage() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const { startUpload, updateProgress, completeUpload } = useUploadProgress();

  const fileCount = useMemo(() => selectedFiles.length, [selectedFiles]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy || fileCount === 0) return;
    setBusy(true);

    try {
      startUpload('file', fileCount);
      const res = await uploadFiles(selectedFiles, '', (event) => {
        updateProgress({
          isActive: event.isUploading,
          type: 'file',
          progress: event.progress,
          uploadedCount: event.successfulFiles + event.failedFiles,
          totalCount: event.totalFiles,
          currentFile: event.currentFile,
        });
      });

      const ok = res.successful.length > 0;
      if (ok) toastSuccess(`Uploaded ${res.successful.length} file(s)`);
      if (res.failed.length > 0) toastError(`${res.failed.length} file(s) failed`);
      completeUpload();
    } catch (err: any) {
      toastError(err?.message || 'Upload failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Upload</h2>
      <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 720 }}>
        <input
          type="file"
          multiple
          onChange={(e) => {
            const list = e.target.files ? Array.from(e.target.files) : [];
            setSelectedFiles(list);
          }}
        />
        <div style={{ fontSize: 12, opacity: 0.8 }}>
          Selected: {fileCount} file(s)
        </div>
        <button disabled={busy || fileCount === 0} type="submit">
          {busy ? 'Uploading...' : 'Upload'}
        </button>
      </form>
    </div>
  );
}

