import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Settings } from 'lucide-react';
import { speechApi } from '../services/api';

interface VoiceInterfaceProps {
  language: string;
  onTranscriptReceived?: (text: string) => void;
  lastMessage?: string;
}

export const VoiceInterface: React.FC<VoiceInterfaceProps> = ({ 
  language, 
  onTranscriptReceived,
  lastMessage 
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordingText, setRecordingText] = useState('');
  const [audioDevices, setAudioDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('');
  const [showDeviceSelector, setShowDeviceSelector] = useState(false);
  const [permissionGranted, setPermissionGranted] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Get available audio input devices
  useEffect(() => {
    const getAudioDevices = async () => {
      try {
        // Request permission first
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        setPermissionGranted(true);
        
        // Stop the permission stream immediately
        stream.getTracks().forEach(track => track.stop());
        
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(device => device.kind === 'audioinput');
        setAudioDevices(audioInputs);
        
        // Set default device
        if (audioInputs.length > 0 && !selectedDeviceId) {
          setSelectedDeviceId(audioInputs[0].deviceId);
        }
      } catch (error) {
        console.error('Error getting audio devices:', error);
        setPermissionGranted(false);
      }
    };

    getAudioDevices();

    // Listen for device changes
    navigator.mediaDevices.addEventListener('devicechange', getAudioDevices);
    
    return () => {
      navigator.mediaDevices.removeEventListener('devicechange', getAudioDevices);
    };
  }, [selectedDeviceId]);

  const startRecording = async () => {
    try {
      // Stop any existing stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }

      const constraints: MediaStreamConstraints = {
        audio: selectedDeviceId 
          ? { deviceId: { exact: selectedDeviceId } }
          : true
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      // Check if the browser supports the preferred audio format
      const options: MediaRecorderOptions = {};
      
      // Try to use formats that Azure Speech SDK can handle better
      if (MediaRecorder.isTypeSupported('audio/wav')) {
        options.mimeType = 'audio/wav';
        console.log('Using audio/wav format');
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=pcm')) {
        options.mimeType = 'audio/webm;codecs=pcm';
        console.log('Using audio/webm;codecs=pcm format');
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        options.mimeType = 'audio/webm;codecs=opus';
        console.log('Using audio/webm;codecs=opus format');
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        options.mimeType = 'audio/webm';
        console.log('Using audio/webm format');
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        options.mimeType = 'audio/mp4';
        console.log('Using audio/mp4 format');
      } else {
        console.log('Using default audio format');
      }

      console.log('MediaRecorder options:', options);

      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const mimeType = mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        await processAudio(audioBlob);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      };

      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
        setRecordingText(language === 'kn' ? 'ರೆಕಾರ್ಡಿಂಗ್ ದೋಷ' : 'Recording error');
        setTimeout(() => setRecordingText(''), 2000);
      };

      mediaRecorder.start(1000); // Collect data every second
      setIsRecording(true);
      setRecordingText(language === 'kn' ? 'ಆಲಿಸುತ್ತಿದ್ದೇನೆ...' : 'Listening...');
    } catch (error) {
      console.error('Error starting recording:', error);
      setRecordingText(
        language === 'kn' 
          ? 'ಮೈಕ್ರೋಫೋನ್ ಪ್ರವೇಶಕ್ಕೆ ಅನುಮತಿ ಬೇಕು'
          : 'Microphone access required'
      );
      setTimeout(() => setRecordingText(''), 3000);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setRecordingText('');
      
      // Stop the stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    try {
      setRecordingText(language === 'kn' ? 'ಪ್ರಕ್ರಿಯೆಗೊಳಿಸುತ್ತಿದ್ದೇನೆ...' : 'Processing...');
      
      console.log('Audio blob details:', {
        size: audioBlob.size,
        type: audioBlob.type
      });

      // Convert blob to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = reader.result as string;
        console.log('Base64 audio length:', base64Audio.length);
        
        // Remove data URL prefix (e.g., "data:audio/webm;base64,")
        const audioBase64 = base64Audio.split(',')[1];
        console.log('Clean base64 length:', audioBase64.length);
        
        if (!audioBase64 || audioBase64.length === 0) {
          console.error('No audio data to send');
          setRecordingText(language === 'kn' ? 'ಆಡಿಯೋ ಡೇಟಾ ಇಲ್ಲ' : 'No audio data');
          setTimeout(() => setRecordingText(''), 2000);
          return;
        }
        
        try {
          console.log('Sending audio to backend...');
          const result = await speechApi.speechToText(audioBase64, language === 'kn' ? 'kn-IN' : 'en-US');
          console.log('Backend response:', result);
          
          if (result.text && result.text.trim()) {
            // Send transcribed text to chat interface
            if (onTranscriptReceived) {
              onTranscriptReceived(result.text);
            }
            setRecordingText(result.text);
            setTimeout(() => setRecordingText(''), 3000);
          } else {
            setRecordingText(language === 'kn' ? 'ಏನೂ ಕೇಳಿಸಲಿಲ್ಲ' : 'No speech detected');
            setTimeout(() => setRecordingText(''), 2000);
          }
        } catch (error) {
          console.error('Speech to text error:', error);
          setRecordingText(language === 'kn' ? 'ತೊಂದರೆ ಆಗಿದೆ' : 'Error processing speech');
          setTimeout(() => setRecordingText(''), 2000);
        }
      };
      
      reader.onerror = (error) => {
        console.error('FileReader error:', error);
        setRecordingText(language === 'kn' ? 'ಫೈಲ್ ಓದುವಲ್ಲಿ ದೋಷ' : 'File reading error');
        setTimeout(() => setRecordingText(''), 2000);
      };
      
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Error processing audio:', error);
    }
  };

  const playResponse = async (text?: string) => {
    try {
      const textToPlay = text || lastMessage;
      if (!textToPlay) {
        console.warn('No text to play');
        return;
      }

      setIsPlaying(true);
      
      const result = await speechApi.textToSpeech(textToPlay, language === 'kn' ? 'kn-IN' : 'en-US');
      
      // Convert base64 to audio and play
      const audioData = `data:audio/wav;base64,${result.audio_base64}`;
      const audio = new Audio(audioData);
      audioRef.current = audio;
      
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => {
        setIsPlaying(false);
        console.error('Error playing audio');
      };
      
      await audio.play();
    } catch (error) {
      console.error('Text to speech error:', error);
      setIsPlaying(false);
    }
  };

  const stopPlaying = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const toggleDeviceSelector = () => {
    setShowDeviceSelector(!showDeviceSelector);
  };

  return (
    <div className="fixed bottom-4 right-4 flex flex-col items-end space-y-2">
      {/* Recording indicator */}
      {recordingText && (
        <div className="bg-white rounded-lg px-3 py-2 shadow-lg border border-agri-green-200 animate-fadeIn max-w-xs">
          <p className="text-sm text-agri-green-700 break-words">{recordingText}</p>
        </div>
      )}
      
      {/* Device selector dropdown */}
      {showDeviceSelector && permissionGranted && audioDevices.length > 1 && (
        <div className="bg-white rounded-lg p-3 shadow-lg border border-agri-green-200 min-w-64">
          <h4 className="text-sm font-medium text-agri-green-700 mb-2">
            {language === 'kn' ? 'ಮೈಕ್ರೋಫೋನ್ ಆಯ್ಕೆ' : 'Select Microphone'}
          </h4>
          <select
            value={selectedDeviceId}
            onChange={(e) => setSelectedDeviceId(e.target.value)}
            className="w-full p-2 text-sm border border-agri-green-200 rounded focus:ring-2 focus:ring-agri-green-500 focus:border-transparent"
          >
            {audioDevices.map((device) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `Microphone ${device.deviceId.slice(0, 5)}...`}
              </option>
            ))}
          </select>
        </div>
      )}
      
      {/* Voice controls */}
      <div className="flex space-x-2">
        {/* Device selector toggle */}
        {permissionGranted && audioDevices.length > 1 && (
          <button
            onClick={toggleDeviceSelector}
            className="p-3 rounded-full shadow-lg bg-white hover:bg-agri-green-50 text-agri-green-600 border border-agri-green-200 transition-all"
            title={language === 'kn' ? 'ಸಾಧನ ಸೆಟ್ಟಿಂಗ್' : 'Device Settings'}
          >
            <Settings className="w-4 h-4" />
          </button>
        )}

        {/* Text to Speech toggle */}
        <button
          onClick={isPlaying ? stopPlaying : () => playResponse()}
          disabled={!lastMessage}
          className={`p-3 rounded-full shadow-lg transition-all ${
            isPlaying 
              ? 'bg-red-500 hover:bg-red-600 text-white' 
              : lastMessage
                ? 'bg-white hover:bg-agri-green-50 text-agri-green-600 border border-agri-green-200'
                : 'bg-gray-200 text-gray-400 border border-gray-300 cursor-not-allowed'
          }`}
          title={isPlaying 
            ? (language === 'kn' ? 'ನಿಲ್ಲಿಸಿ' : 'Stop') 
            : (language === 'kn' ? 'ಕೇಳಿ' : 'Listen')
          }
        >
          {isPlaying ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
        </button>

        {/* Speech to Text toggle */}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!permissionGranted}
          className={`p-4 rounded-full shadow-lg transition-all ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse' 
              : permissionGranted
                ? 'bg-agri-green-600 hover:bg-agri-green-700 text-white'
                : 'bg-gray-200 text-gray-400 border border-gray-300 cursor-not-allowed'
          }`}
          title={
            !permissionGranted
              ? (language === 'kn' ? 'ಮೈಕ್ರೋಫೋನ್ ಅನುಮತಿ ಬೇಕು' : 'Microphone permission required')
              : isRecording 
                ? (language === 'kn' ? 'ನಿಲ್ಲಿಸಿ' : 'Stop Recording') 
                : (language === 'kn' ? 'ಮಾತನಾಡಿ' : 'Start Recording')
          }
        >
          {isRecording ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
        </button>
      </div>
      
      {/* Permission warning */}
      {!permissionGranted && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 max-w-xs">
          <p className="text-xs text-yellow-700">
            {language === 'kn' 
              ? 'ಮೈಕ್ರೋಫೋನ್ ಪ್ರವೇಶಕ್ಕೆ ಅನುಮತಿ ನೀಡಿ'
              : 'Please allow microphone access for voice features'
            }
          </p>
        </div>
      )}
    </div>
  );
};
