import React, { useState } from 'react';
import DublinCoreView from './DublinCoreView';
import Marc21View from './Marc21View';
import Alert from './Alert';

export default function MetadataResults({ jobsData, onBack, onStartOver }) {
  const [activeFileTab, setActiveFileTab] = useState(0);
  const [formatTab, setFormatTab] = useState('dublinCore'); // 'dublinCore' | 'marc21'
  
  // Local state for editable metadata to allow saving changes
  const [editedMetadata, setEditedMetadata] = useState(
    jobsData.reduce((acc, job, idx) => ({ ...acc, [idx]: job.metadata || {} }), {})
  );
  
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const activeJob = jobsData[activeFileTab];
  const activeMeta = editedMetadata[activeFileTab];

  const handleMetaChange = (field, value) => {
    setEditedMetadata({
      ...editedMetadata,
      [activeFileTab]: {
        ...editedMetadata[activeFileTab],
        [field]: value
      }
    });
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const res = await fetch(`/api/process/${activeJob.job_id}/metadata`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(activeMeta)
      });
      if (!res.ok) throw new Error('Failed to save metadata');
      const updatedJob = await res.json();
      
      activeJob.dublin_core_xml = updatedJob.dublin_core_xml;
      activeJob.marc21_mrk = updatedJob.marc21_mrk;
      
      setMessage({ type: 'success', text: 'Metadata saved and records updated successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to save' });
    } finally {
      setSaving(false);
    }
  };

  const getConfidenceBadge = (confidenceStr) => {
    const conf = (confidenceStr || 'high').toLowerCase();
    if (conf === 'high') return <span className="badge confidence-high">High</span>;
    if (conf === 'medium') return <span className="badge confidence-medium">Medium</span>;
    return <span className="badge confidence-low">Low</span>;
  };

  return (
    <div className="card fade-in slide-in-right">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2>Results & Export</h2>
        <button className="btn btn-secondary" onClick={onStartOver}>Start Over</button>
      </div>

      {message && <Alert type={message.type} message={message.text} onClose={() => setMessage(null)} />}

      {jobsData.length > 1 && (
        <div className="tab-container">
          {jobsData.map((job, idx) => (
            <button 
              key={job.job_id}
              className={`tab ${idx === activeFileTab ? 'active' : ''}`}
              onClick={() => setActiveFileTab(idx)}
            >
              {job.filename}
            </button>
          ))}
        </div>
      )}

      <div className="side-by-side" style={{ marginBottom: '2rem' }}>
        <div className="metadata-form">
          <h3 style={{ marginBottom: '1rem' }}>Extracted Metadata</h3>
          
          {Object.entries(activeMeta).map(([key, value]) => {
            if (key === 'confidence_scores' || typeof value === 'object' && !Array.isArray(value)) return null;
            
            const displayValue = Array.isArray(value) ? value.join('; ') : (value || '');
            const confidence = activeMeta.confidence_scores?.[key] || 'high';
            
            return (
              <div key={key} className="metadata-field">
                <div className="metadata-label">
                  <span style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}</span>
                  {getConfidenceBadge(confidence)}
                </div>
                <input 
                  type="text" 
                  className="metadata-value" 
                  value={displayValue}
                  onChange={(e) => handleMetaChange(key, e.target.value)}
                />
              </div>
            );
          })}
          
          <button className="btn btn-primary" onClick={handleSave} disabled={saving} style={{ marginTop: '1rem' }}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        <div>
          <div className="tab-container">
            <button 
              className={`tab ${formatTab === 'dublinCore' ? 'active' : ''}`}
              onClick={() => setFormatTab('dublinCore')}
            >
              Dublin Core
            </button>
            <button 
              className={`tab ${formatTab === 'marc21' ? 'active' : ''}`}
              onClick={() => setFormatTab('marc21')}
            >
              MARC 21
            </button>
          </div>

          <div style={{ marginTop: '1rem' }}>
            {formatTab === 'dublinCore' ? (
              <DublinCoreView 
                xml={activeJob.dublin_core_xml || '<xml></xml>'} 
                json={activeMeta}
                jobId={activeJob.job_id} 
              />
            ) : (
              <Marc21View 
                mrk={activeJob.marc21_mrk || ''} 
                json={activeMeta}
                jobId={activeJob.job_id} 
              />
            )}
          </div>
        </div>
      </div>

      <div className="actions-row">
        <button className="btn btn-secondary" onClick={onBack}>
          Back
        </button>
      </div>
    </div>
  );
}
