import React, { useState } from 'react';
import Alert from './Alert';

export default function TextReview({ jobsData, onBack, onContinue }) {
  const [activeTab, setActiveTab] = useState(0);
  const [texts, setTexts] = useState(
    jobsData.reduce((acc, job, idx) => ({ ...acc, [idx]: job.extracted_text || '' }), {})
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const activeJob = jobsData[activeTab];

  const handleTextChange = (e) => {
    setTexts({ ...texts, [activeTab]: e.target.value });
  };

  const handleContinue = async () => {
    setSaving(true);
    setError(null);
    try {
      const results = [];
      // Save text and get metadata for each job
      for (let i = 0; i < jobsData.length; i++) {
        const job = jobsData[i];
        
        // 1. Update text
        const updateRes = await fetch(`/api/process/${job.job_id}/text`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: texts[i] })
        });
        
        if (!updateRes.ok) throw new Error(`Failed to update text for ${job.filename}`);
        
        const updatedJobData = await updateRes.json();
        results.push(updatedJobData);
      }
      
      onContinue(results);
    } catch (err) {
      setError(err.message || 'Failed to save texts and extract metadata');
    } finally {
      setSaving(false);
    }
  };

  const wordCount = texts[activeTab].trim() ? texts[activeTab].trim().split(/\s+/).length : 0;
  const charCount = texts[activeTab].length;

  return (
    <div className="card fade-in slide-in-right">
      <h2>Review Extracted Text</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        Review and edit the extracted text before generating metadata.
      </p>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      {jobsData.length > 1 && (
        <div className="tab-container">
          {jobsData.map((job, idx) => (
            <button 
              key={job.job_id}
              className={`tab ${idx === activeTab ? 'active' : ''}`}
              onClick={() => setActiveTab(idx)}
            >
              {job.filename}
            </button>
          ))}
        </div>
      )}

      <div className="side-by-side" style={{ marginBottom: '2rem' }}>
        <div>
          <h3 style={{ marginBottom: '1rem' }}>Original File</h3>
          <div className="file-card" style={{ marginBottom: '1rem' }}>
            <div className="file-info">
              <span style={{ fontSize: '1.5rem' }}>📄</span>
              <div>
                <div className="file-name">{activeJob.filename}</div>
                <div className="file-size">{activeJob.file_type || 'Document'}</div>
              </div>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <span className="badge confidence-high">English ✓</span>
            {activeJob.ocr_used && (
              <span className={`badge ${activeJob.confidence > 80 ? 'confidence-high' : 'confidence-medium'}`}>
                OCR Used ({activeJob.confidence || 0}%)
              </span>
            )}
          </div>
          
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            <p>Words: {wordCount}</p>
            <p>Characters: {charCount}</p>
          </div>
        </div>

        <div>
          <h3 style={{ marginBottom: '1rem' }}>Extracted Text</h3>
          <textarea 
            className="text-editor"
            value={texts[activeTab]}
            onChange={handleTextChange}
            placeholder="No text extracted..."
          />
        </div>
      </div>

      <div className="actions-row">
        <button className="btn btn-secondary" onClick={onBack} disabled={saving}>
          Back
        </button>
        <button className="btn btn-primary" onClick={handleContinue} disabled={saving}>
          {saving ? (
            <>
              <div className="spinner"></div>
              Processing...
            </>
          ) : 'Accept & Continue'}
        </button>
      </div>
    </div>
  );
}
