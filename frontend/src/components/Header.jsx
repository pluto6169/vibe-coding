import React from 'react';
import ThemeToggle from './ThemeToggle';

export default function Header() {
  return (
    <header className="header">
      <div className="container header-content">
        <div className="logo-area">
          <div className="logo-icon">📚</div>
          <div className="logo-text">
            <h1>MetaScholar</h1>
            <p>Academic Article Metadata Extractor</p>
          </div>
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
}
