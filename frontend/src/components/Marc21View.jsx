import React, { useState } from 'react';
import Alert from './Alert';

export default function Marc21View({ mrk, json, jobId }) {
  const [copied, setCopied] = useState(false);

  const downloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(mrk);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  // Simple MRK syntax highlighting logic
  const highlightMrk = (mrkString) => {
    if (!mrkString) return '';
    
    const lines = mrkString.split('\n');
    const highlighted = lines.map(line => {
      // Match typical MRK format: =TAG  IND1IND2 $aValue
      const match = line.match(/^=([0-9]{3})\s+([\\0-9a-zA-Z\s]{2})?(.*)$/);
      if (match) {
        const tag = match[1];
        const inds = match[2] || '  ';
        let subfields = match[3] || '';
        
        // Highlight subfields
        subfields = subfields.replace(/(\$[a-z0-9])/g, '<span class="mrk-sub">$1</span>');
        
        return `=<span class="mrk-tag">${tag}</span>  <span class="mrk-ind">${inds.replace(/\\/g, ' ')}</span>${subfields}`;
      }
      return line;
    });
      
    return { __html: highlighted.join('\n') };
  };

  return (
    <div>
      <div className="draft-banner">
        ⚠️ This is a preliminary record. Professional cataloger review is required.
      </div>
      
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <button 
          className="btn btn-secondary btn-icon" 
          onClick={() => downloadFile(mrk, `record_${jobId}.mrk`, 'text/plain')}
          title="Download .mrk"
        >
          ⬇️ MRK
        </button>
        <button 
          className="btn btn-secondary btn-icon" 
          onClick={() => downloadFile(JSON.stringify(json, null, 2), `record_${jobId}.json`, 'application/json')}
          title="Download JSON"
        >
          ⬇️ JSON
        </button>
        <button 
          className="btn btn-secondary btn-icon" 
          onClick={handleCopy}
          title="Copy to clipboard"
        >
          {copied ? '✅ Copied' : '📋 Copy'}
        </button>
      </div>
      
      {copied && <Alert type="success" message="MRK copied to clipboard!" onClose={() => setCopied(false)} />}
      
      <div 
        className="mrk-display fade-in" 
        dangerouslySetInnerHTML={highlightMrk(mrk)} 
      />
    </div>
  );
}
