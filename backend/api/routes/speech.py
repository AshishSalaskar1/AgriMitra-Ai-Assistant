from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import azure.cognitiveservices.speech as speechsdk
import io
import base64
import logging

from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

class SpeechToTextRequest(BaseModel):
    audio_base64: str
    language: Optional[str] = "en-US"  # Default to English

class TextToSpeechRequest(BaseModel):
    text: str
    language: Optional[str] = "en-US"
    voice: Optional[str] = None

class SpeechResponse(BaseModel):
    text: str
    confidence: Optional[float] = None

class AudioResponse(BaseModel):
    audio_base64: str
    format: str = "wav"

class AzureSpeechService:
    def __init__(self):
        self.speech_key = settings.azure_speech_key
        self.speech_region = settings.azure_speech_region
        
        # Configure speech service
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        
        # Language mappings
        self.language_mappings = {
            "en": "en-US",
            "kn": "kn-IN",  # Kannada
            "hi": "hi-IN",  # Hindi
            "ta": "ta-IN"   # Tamil
        }
        
        self.voice_mappings = {
            "en-US": "en-US-AriaNeural",
            "kn-IN": "kn-IN-SapnaNeural",
            "hi-IN": "hi-IN-SwaraNeural",
            "ta-IN": "ta-IN-PallaviNeural"
        }

    async def speech_to_text(self, audio_data: bytes, language: str = "en-US") -> dict:
        """Convert speech to text using Azure Speech Services"""
        try:
            # Map language code
            full_language = self.language_mappings.get(language, language)
            logger.info(f"Processing speech-to-text for language: {language} -> {full_language}")
            logger.info(f"Audio data size: {len(audio_data)} bytes")
            
            # Configure recognition
            self.speech_config.speech_recognition_language = full_language
            
            # Method 1: Try with audio format specification
            try:
                # Set audio format for better compatibility
                audio_format = speechsdk.audio.AudioStreamFormat(
                    samples_per_second=16000,  # 16 kHz
                    bits_per_sample=16,        # 16-bit
                    channels=1                 # Mono
                )
                
                # Create audio stream from bytes with format specification
                audio_stream = speechsdk.audio.PushAudioInputStream(stream_format=audio_format)
                audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
                
                # Create recognizer
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
                
                # Push audio data
                audio_stream.write(audio_data)
                audio_stream.close()
                
                # Perform recognition
                logger.info("Starting speech recognition with format specification...")
                result = speech_recognizer.recognize_once()
                
                if result.reason == speechsdk.ResultReason.RecognizedSpeech and result.text.strip():
                    logger.info(f"Success with format specification: '{result.text}'")
                    return self._process_recognition_result(result)
                    
            except Exception as format_error:
                logger.warning(f"Format-specific recognition failed: {format_error}")
            
            # Method 2: Try without format specification (fallback)
            try:
                logger.info("Trying fallback method without format specification...")
                
                # Create audio stream without format specification
                audio_stream = speechsdk.audio.PushAudioInputStream()
                audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
                
                # Create recognizer
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
                
                # Push audio data
                audio_stream.write(audio_data)
                audio_stream.close()
                
                # Perform recognition
                result = speech_recognizer.recognize_once()
                
                return self._process_recognition_result(result)
                
            except Exception as fallback_error:
                logger.error(f"Fallback recognition failed: {fallback_error}")
                raise fallback_error
                
        except Exception as e:
            logger.error(f"Speech to text error: {str(e)}")
            raise e
    
    def _process_recognition_result(self, result) -> dict:
        """Process the recognition result and return structured data"""
        logger.info(f"Recognition result reason: {result.reason}")
        logger.info(f"Recognition result text: '{result.text}'")
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Try to get confidence from detailed results
            confidence = 0.0
            try:
                if hasattr(result, 'properties') and result.properties:
                    detailed_result = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
                    if detailed_result:
                        import json
                        parsed = json.loads(detailed_result)
                        if 'NBest' in parsed and len(parsed['NBest']) > 0:
                            confidence = parsed['NBest'][0].get('Confidence', 0.0)
            except Exception as conf_error:
                logger.warning(f"Could not extract confidence: {conf_error}")
            
            return {
                "text": result.text,
                "confidence": confidence
            }
        elif result.reason == speechsdk.ResultReason.NoMatch:
            logger.warning("No speech could be recognized")
            return {"text": "", "confidence": 0.0}
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Speech recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.error(f"Error details: {cancellation_details.error_details}")
            return {"text": "", "confidence": 0.0}
        else:
            logger.warning(f"Unexpected result reason: {result.reason}")
            return {"text": "", "confidence": 0.0}

    async def text_to_speech(self, text: str, language: str = "en-US", voice: str = None) -> bytes:
        """Convert text to speech using Azure Speech Services"""
        try:
            # Map language and voice
            full_language = self.language_mappings.get(language, language)
            if not voice:
                voice = self.voice_mappings.get(full_language, "en-US-AriaNeural")
            
            # Configure synthesis
            self.speech_config.speech_synthesis_voice_name = voice
            
            # Create synthesizer with memory stream
            audio_stream = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )
            
            # Perform synthesis
            result = speech_synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                raise Exception(f"Speech synthesis failed: {result.reason}")
                
        except Exception as e:
            logger.error(f"Text to speech error: {str(e)}")
            raise e

# Initialize service
speech_service = AzureSpeechService()

@router.post("/speech-to-text", response_model=SpeechResponse)
async def convert_speech_to_text(request: SpeechToTextRequest):
    """Convert audio to text"""
    try:
        # Debug: Check if audio data is received
        logger.info(f"Received audio data length: {len(request.audio_base64)} characters")
        logger.info(f"Language: {request.language}")
        
        # Decode base64 audio
        audio_data = base64.b64decode(request.audio_base64)
        logger.info(f"Decoded audio data length: {len(audio_data)} bytes")
        
        # Process with Azure Speech
        result = await speech_service.speech_to_text(
            audio_data=audio_data,
            language=request.language
        )
        
        logger.info(f"Speech recognition result: {result}")
        
        return SpeechResponse(
            text=result["text"],
            confidence=result["confidence"]
        )
        
    except Exception as e:
        logger.error(f"Error in speech to text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(e)}")

@router.post("/text-to-speech", response_model=AudioResponse)
async def convert_text_to_speech(request: TextToSpeechRequest):
    """Convert text to audio"""
    try:
        # Generate audio with Azure Speech
        audio_data = await speech_service.text_to_speech(
            text=request.text,
            language=request.language,
            voice=request.voice
        )
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        return AudioResponse(
            audio_base64=audio_base64,
            format="wav"
        )
        
    except Exception as e:
        logger.error(f"Error in text to speech: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": "en", "name": "English", "full_code": "en-US"},
            {"code": "kn", "name": "ಕನ್ನಡ (Kannada)", "full_code": "kn-IN"},
            {"code": "hi", "name": "हिन्दी (Hindi)", "full_code": "hi-IN"},
            {"code": "ta", "name": "தமிழ் (Tamil)", "full_code": "ta-IN"}
        ]
    }
