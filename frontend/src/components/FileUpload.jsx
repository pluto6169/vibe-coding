import React, { useState, useRef } from 'react';
import { useFileUpload } from '../hooks/useFileUpload';
import Alert from './Alert';

export default function FileUpload({ onFilesProcessed }) {
  const { files, uploading, uploadProgress, error, addFiles, removeFile, uploadFiles } = useFileUpload();
  const [isDragOver, setIsDragOver] = useState(false);
  const [processingStage, setProcessingStage] = useState('');
  const fileInputRef = useRef(null);
  const [localError, setLocalError] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      addFiles(e.target.files);
    }
  };

  const getFileIcon = (type) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('word') || type.includes('document')) return '📝';
    if (type.includes('image')) return '🖼️';
    return '📁';
  };

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleProcess = async () => {
    setLocalError(null);
    setProcessingStage('Uploading files...');
    const result = await uploadFiles();
    
    if (result && Array.isArray(result) && result.length > 0) {
      setProcessingStage('Processing files...');
      
      try {
        const jobResults = [];
        for (const item of result) {
          const job_id = item.job_id;
          const res = await fetch(`/api/process/${job_id}`, {
            method: 'POST'
          });
          if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `Failed to process ${item.filename}`);
          }
          const jobData = await res.json();
          jobResults.push(jobData);
        }
        
        onFilesProcessed(jobResults);
      } catch (err) {
        setLocalError(err.message || 'Error processing files');
        setProcessingStage('');
      }
    } else {
      setProcessingStage('');
    }
  };

  const displayError = error || localError;

  return (
    <div className="card fade-in">
      <h2>Upload Documents</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        Upload PDF, Word, TXT, or Image files to extract metadata.
      </p>

      {displayError && <Alert type="error" message={displayError} onClose={() => setLocalError(null)} />}

      <div 
        className={`upload-zone ${isDragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <div className="upload-icon">📁</div>
        <h3>Drag & drop files here</h3>
        <p>or click to browse from your computer</p>
        <input 
          type="file" 
          multiple 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleFileInput}
          accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png"
        />
      </div>

      {files.length > 0 && (
        <div className="file-list fade-in">
          <h3>Selected Files ({files.length})</h3>
          {files.map((fileObj, index) => (
            <div key={fileObj.id} className="file-card">
              <div className="file-info">
                <span style={{ fontSize: '1.5rem' }}>{getFileIcon(fileObj.type)}</span>
                <div>
                  <div className="file-name">{fileObj.name}</div>
                  <div className="file-size">{formatSize(fileObj.size)}</div>
                </div>
              </div>
              <button 
                className="btn-icon" 
                onClick={() => removeFile(index)}
                disabled={uploading}
                title="Remove file"
              >
                ❌
              </button>
            </div>
          ))}
          
          {(uploading || processingStage) && (
            <div style={{ marginTop: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span>{processingStage}</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
              </div>
            </div>
          )}

          <div className="actions-row">
            <button 
              className="btn btn-primary" 
              onClick={handleProcess} 
              disabled={uploading || files.length === 0}
            >
              {uploading || processingStage ? (
                <>
                  <div className="spinner"></div>
                  Processing...
                </>
              ) : 'Process Files'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
