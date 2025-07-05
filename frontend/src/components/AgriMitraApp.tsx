import React, { useState } from 'react';
import { Header } from './Header';
import { ChatInterface } from './ChatInterface';
import { SidePanel } from './SidePanel';
import { VoiceInterface } from './VoiceInterface';

export const AgriMitraApp: React.FC = () => {
  const [showSidePanel, setShowSidePanel] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [lastAssistantMessage, setLastAssistantMessage] = useState<string>('');
  const [voiceTranscript, setVoiceTranscript] = useState<string>('');

  const handleVoiceTranscript = (transcript: string) => {
    setVoiceTranscript(transcript);
  };

  const handleVoiceTranscriptProcessed = () => {
    setVoiceTranscript('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-agri-green-50 to-agri-green-100">
      <Header 
        onToggleSidePanel={() => setShowSidePanel(!showSidePanel)}
        currentLanguage={currentLanguage}
        onLanguageChange={setCurrentLanguage}
      />
      
      <div className="flex h-screen pt-16">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col relative">
          <ChatInterface 
            language={currentLanguage}
            onLastMessageChange={setLastAssistantMessage}
            voiceTranscript={voiceTranscript}
            onVoiceTranscriptProcessed={handleVoiceTranscriptProcessed}
          />
          <VoiceInterface 
            language={currentLanguage}
            onTranscriptReceived={handleVoiceTranscript}
            lastMessage={lastAssistantMessage}
          />
        </div>
        
        {/* Side Panel */}
        {showSidePanel && (
          <SidePanel 
            onClose={() => setShowSidePanel(false)}
            language={currentLanguage}
          />
        )}
      </div>
    </div>
  );
};
