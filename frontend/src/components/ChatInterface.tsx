import React, { useState, useRef, useEffect } from 'react';
import { Send, Image as ImageIcon, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { chatApi } from '../services/api';
import type { ChatMessage } from '../types';

interface ChatInterfaceProps {
  language: string;
  onLastMessageChange?: (message: string) => void;
  voiceTranscript?: string;
  onVoiceTranscriptProcessed?: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  language, 
  onLastMessageChange,
  voiceTranscript,
  onVoiceTranscriptProcessed 
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: language === 'kn' 
        ? 'ನಮಸ್ಕಾರ! ನಾನು AgriMitra. ನಿಮ್ಮ ಕೃಷಿ ಸಂಬಂಧಿ ಯಾವುದೇ ಪ್ರಶ್ನೆಗಳಿಗೆ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧ. ಬೆಳೆ ಸಮಸ್ಯೆಗಳು, ಮಾರುಕಟ್ಟೆ ದರಗಳು, ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ!'
        : 'Hello! I\'m AgriMitra, your agricultural assistant. I can help with crop diseases, market prices, government schemes, and farming advice. How can I assist you today?',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle voice transcript
  useEffect(() => {
    if (voiceTranscript && voiceTranscript.trim()) {
      setInputMessage(voiceTranscript);
      if (onVoiceTranscriptProcessed) {
        onVoiceTranscriptProcessed();
      }
    }
  }, [voiceTranscript, onVoiceTranscriptProcessed]);

  // Notify parent about last assistant message for voice playback
  useEffect(() => {
    const lastAssistantMessage = messages
      .filter(msg => msg.role === 'assistant')
      .pop();
    
    if (lastAssistantMessage && onLastMessageChange) {
      onLastMessageChange(lastAssistantMessage.content);
    }
  }, [messages, onLastMessageChange]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && !selectedImage) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage || 'Image uploaded for analysis',
      timestamp: new Date().toISOString(),
      imageUrl: previewUrl
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      let response;
      
      if (selectedImage) {
        // Handle image analysis
        const uploadResponse = await chatApi.uploadImage(selectedImage);
        const analysisResponse = await chatApi.analyzeImage(
          uploadResponse.image_base64,
          inputMessage || 'Analyze this crop image for diseases or issues',
          language
        );
        
        response = {
          response: analysisResponse.analysis,
          suggested_actions: analysisResponse.recommended_actions || []
        };
      } else {
        // Handle text message
        response = await chatApi.sendMessage(inputMessage, messages, language);
      }

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Clear image after processing
      if (selectedImage) {
        setSelectedImage(null);
        setPreviewUrl('');
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: language === 'kn'
          ? 'ಕ್ಷಮಿಸಿ, ಈ ಸಮಯದಲ್ಲಿ ತೊಂದರೆ ಆಗುತ್ತಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.'
          : 'Sorry, I\'m having trouble right now. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-white/50 backdrop-blur-sm">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-agri-green-600 text-white'
                  : 'bg-white border border-agri-green-200 text-agri-green-900'
              }`}
            >
              {message.imageUrl && (
                <img
                  src={message.imageUrl}
                  alt="Uploaded"
                  className="max-w-full h-auto rounded-lg mb-2"
                />
              )}
              {message.role === 'assistant' ? (
                <div className="chat-markdown">
                  <ReactMarkdown 
                    components={{
                      p: ({ children }) => <p>{children}</p>,
                      ul: ({ children }) => <ul className="list-disc list-inside">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside">{children}</ol>,
                      li: ({ children }) => <li>{children}</li>,
                      strong: ({ children }) => <strong>{children}</strong>,
                      em: ({ children }) => <em>{children}</em>,
                      h1: ({ children }) => <h1 className="text-lg font-bold">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-base font-bold">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-sm font-bold">{children}</h3>,
                      code: ({ children }) => <code>{children}</code>,
                      blockquote: ({ children }) => <blockquote>{children}</blockquote>
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </p>
              )}
              <span className="text-xs opacity-70 mt-1 block">
                {new Date(message.timestamp || '').toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start animate-fadeIn">
            <div className="bg-white border border-agri-green-200 rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-agri-green-600" />
                <span className="text-sm text-agri-green-700">
                  {language === 'kn' ? 'ಯೋಚಿಸುತ್ತಿದ್ದೇನೆ...' : 'Thinking...'}
                </span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Image Preview */}
      {previewUrl && (
        <div className="px-4 py-2 border-t border-agri-green-200">
          <div className="relative inline-block">
            <img
              src={previewUrl}
              alt="Preview"
              className="w-20 h-20 object-cover rounded-lg border-2 border-agri-green-300"
            />
            <button
              onClick={() => {
                setSelectedImage(null);
                setPreviewUrl('');
              }}
              className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full text-xs flex items-center justify-center hover:bg-red-600"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-agri-green-200 p-4">
        <div className="flex items-end space-x-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex-shrink-0 p-2 text-agri-green-600 hover:bg-agri-green-100 rounded-lg transition-colors"
            title={language === 'kn' ? 'ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ' : 'Upload Image'}
          >
            <ImageIcon className="w-5 h-5" />
          </button>
          
          <div className="flex-1 relative">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                language === 'kn'
                  ? 'ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...'
                  : 'Type your question here...'
              }
              className="w-full px-3 py-2 border border-agri-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-agri-green-500 focus:border-transparent resize-none"
              rows={1}
              style={{ minHeight: '40px', maxHeight: '120px' }}
            />
          </div>
          
          <button
            onClick={handleSendMessage}
            disabled={isLoading || (!inputMessage.trim() && !selectedImage)}
            className="flex-shrink-0 p-2 bg-agri-green-600 text-white rounded-lg hover:bg-agri-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleImageSelect}
        className="hidden"
      />
    </div>
  );
};
