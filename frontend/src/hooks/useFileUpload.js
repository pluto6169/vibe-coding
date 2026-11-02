import { useState } from 'react';

export function useFileUpload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const addFiles = (fileList) => {
    const newFiles = Array.from(fileList).map(file => ({
      file,
      id: Math.random().toString(36).substring(7),
      name: file.name,
      size: file.size,
      type: file.type
    }));
    setFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return null;
    
    setUploading(true);
    setError(null);
    setUploadProgress(10);
    
    const formData = new FormData();
    files.forEach(f => formData.append('files', f.file));
    
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      setUploadProgress(50);
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      
      const data = await response.json();
      setUploadProgress(100);
      return data; // { job_ids: [...] }
    } catch (err) {
      setError(err.message || 'An error occurred during upload');
      return null;
    } finally {
      setUploading(false);
    }
  };

  return { files, uploading, uploadProgress, error, addFiles, removeFile, uploadFiles };
}
