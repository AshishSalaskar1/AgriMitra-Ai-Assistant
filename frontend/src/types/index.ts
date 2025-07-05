export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  imageUrl?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id?: string;
  suggested_actions?: string[];
}

export interface ImageAnalysisResponse {
  analysis: string;
  disease_detected?: string;
  confidence_score?: number;
  recommended_actions?: string[];
  local_remedies?: string[];
}

export interface MarketPrice {
  crop_name: string;
  current_price: number;
  price_unit: string;
  market_name: string;
  price_date: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  trend_percentage?: number;
  recommendations?: string[];
}

export interface GovernmentScheme {
  name: string;
  description: string;
  category: string;
  eligibility: string[];
  benefits: string[];
  application_process: string[];
  documents_required: string[];
  application_link?: string;
  deadline?: string;
  contact_info?: Record<string, string>;
}
