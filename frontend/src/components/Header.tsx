import React from 'react';
import { Menu, Globe, Leaf } from 'lucide-react';

interface HeaderProps {
  onToggleSidePanel: () => void;
  currentLanguage: string;
  onLanguageChange: (language: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  onToggleSidePanel, 
  currentLanguage, 
  onLanguageChange 
}) => {
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'kn', name: 'ಕನ್ನಡ' },
    { code: 'hi', name: 'हिन्दी' },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-agri-green-200 shadow-sm">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Left side - Menu and Logo */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleSidePanel}
            className="p-2 rounded-lg hover:bg-agri-green-100 transition-colors"
          >
            <Menu className="w-6 h-6 text-agri-green-700" />
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-agri-green-600 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-agri-green-800">AgriMitra</h1>
              <p className="text-xs text-agri-green-600">Your Agricultural Assistant</p>
            </div>
          </div>
        </div>

        {/* Right side - Language selector */}
        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-agri-green-600" />
          <select
            value={currentLanguage}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="bg-transparent border border-agri-green-300 rounded-md px-2 py-1 text-sm text-agri-green-700 focus:outline-none focus:ring-2 focus:ring-agri-green-500"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  );
};
