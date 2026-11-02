import React from 'react';
import { useTheme } from '../hooks/useTheme';

export default function ThemeToggle() {
  const [theme, toggleTheme] = useTheme();

  return (
    <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
}
