import React, { useEffect } from 'react';

export default function Alert({ type = 'info', message, onClose }) {
  useEffect(() => {
    if (onClose) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [onClose]);

  const icons = {
    error: '❌',
    warning: '⚠️',
    success: '✅',
    info: 'ℹ️'
  };

  return (
    <div className={`alert alert-${type}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span>{icons[type]}</span>
        <span>{message}</span>
      </div>
      {onClose && (
        <button onClick={onClose} className="btn-icon">
          ✕
        </button>
      )}
    </div>
  );
}
