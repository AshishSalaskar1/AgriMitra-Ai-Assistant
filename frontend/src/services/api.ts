import axios from 'axios';
import type { ChatMessage, ChatResponse, ImageAnalysisResponse, MarketPrice, GovernmentScheme } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  sendMessage: async (message: string, history: ChatMessage[], language: string = 'en'): Promise<ChatResponse> => {
    const response = await api.post('/chat/message', {
      message,
      conversation_history: history,
      language
    });
    return response.data;
  },

  analyzeImage: async (imageBase64: string, query: string = '', language: string = 'en'): Promise<ImageAnalysisResponse> => {
    const response = await api.post('/chat/analyze-image', {
      image_base64: imageBase64,
      query,
      language
    });
    return response.data;
  },

  uploadImage: async (file: File): Promise<{ image_base64: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/chat/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};

export const speechApi = {
  speechToText: async (audioBase64: string, language: string = 'en-US'): Promise<{ text: string; confidence?: number }> => {
    const response = await api.post('/speech/speech-to-text', {
      audio_base64: audioBase64,
      language
    });
    return response.data;
  },

  textToSpeech: async (text: string, language: string = 'en-US'): Promise<{ audio_base64: string }> => {
    const response = await api.post('/speech/text-to-speech', {
      text,
      language
    });
    return response.data;
  },

  getSupportedLanguages: async (): Promise<{ languages: Array<{ code: string; name: string; full_code: string }> }> => {
    const response = await api.get('/speech/supported-languages');
    return response.data;
  }
};

export const marketApi = {
  getCropPrice: async (cropName: string, location: string = 'Karnataka'): Promise<MarketPrice> => {
    const response = await api.get(`/market/price/${cropName}`, {
      params: { location }
    });
    return response.data;
  },

  getMarketTrends: async (cropName: string, days: number = 7) => {
    const response = await api.get(`/market/trends/${cropName}`, {
      params: { days }
    });
    return response.data;
  },

  getPopularCrops: async () => {
    const response = await api.get('/market/popular-crops');
    return response.data;
  },

  analyzeSelling: async (cropName: string, location: string = 'Karnataka') => {
    const response = await api.post('/market/analyze-selling-decision', {
      crop_name: cropName,
      location
    });
    return response.data;
  }
};

export const schemesApi = {
  searchSchemes: async (query: string, state: string = 'Karnataka', category?: string): Promise<{ schemes: GovernmentScheme[]; total_found: number }> => {
    const response = await api.get('/schemes/search', {
      params: { query, state, category }
    });
    return response.data;
  },

  getSchemeCategories: async () => {
    const response = await api.get('/schemes/categories');
    return response.data;
  },

  getPopularSchemes: async () => {
    const response = await api.get('/schemes/popular');
    return response.data;
  },

  getSchemeDetails: async (schemeName: string): Promise<GovernmentScheme> => {
    const response = await api.get(`/schemes/scheme/${schemeName}`);
    return response.data;
  }
};
