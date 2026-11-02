import React, { useState } from 'react';
import Alert from './Alert';

export default function DublinCoreView({ xml, json, jobId }) {
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
    navigator.clipboard.writeText(xml);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  // Simple XML syntax highlighting logic
  const highlightXml = (xmlString) => {
    if (!xmlString) return '';
    
    // This is a basic approach, a real app might use PrismJS or similar
    const formatted = xmlString
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/&lt;(\/?[a-zA-Z0-9:-]+)/g, '&lt;<span class="xml-tag">$1</span>')
      .replace(/([a-zA-Z0-9:-]+)="([^"]*)"/g, '<span class="xml-attr">$1</span>="<span class="xml-val">$2</span>"');
      
    return { __html: formatted };
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <button 
          className="btn btn-secondary btn-icon" 
          onClick={() => downloadFile(xml, `metadata_${jobId}.xml`, 'application/xml')}
          title="Download XML"
        >
          ⬇️ XML
        </button>
        <button 
          className="btn btn-secondary btn-icon" 
          onClick={() => downloadFile(JSON.stringify(json, null, 2), `metadata_${jobId}.json`, 'application/json')}
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
      
      {copied && <Alert type="success" message="XML copied to clipboard!" onClose={() => setCopied(false)} />}
      
      <div 
        className="xml-display fade-in" 
        dangerouslySetInnerHTML={highlightXml(xml)} 
      />
    </div>
  );
}
