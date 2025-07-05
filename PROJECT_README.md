# AgriMitra - AI-Powered Agricultural Assistant

AgriMitra is an intelligent agricultural assistant built to help farmers with crop disease diagnosis, market analysis, and government scheme navigation. The application uses Azure AI services with LangChain for intelligent responses and provides both text and voice interfaces for accessibility.

## 🌱 Features

### Core Capabilities
- **Crop Disease Diagnosis**: Upload images of affected plants for AI-powered disease identification and treatment recommendations
- **Market Price Analysis**: Real-time market prices, trends, and selling decision guidance
- **Government Schemes**: Information about agricultural subsidies, loans, insurance, and training programs
- **Voice Interface**: Speech-to-text and text-to-speech for hands-free interaction
- **Multilingual Support**: English, Kannada, Hindi, and Tamil support

### Key Technologies
- **Frontend**: React + TypeScript, Tailwind CSS, Vite
- **Backend**: Python + FastAPI, LangChain
- **AI Services**: Azure OpenAI (GPT-4o), Azure Speech Services
- **Voice Processing**: Azure Cognitive Speech Services
- **Image Analysis**: Azure Computer Vision (integrated with LangChain)

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.9 or higher)
- Azure AI services account (OpenAI + Speech Services)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your Azure credentials:
   ```env
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   AZURE_SPEECH_KEY=your_azure_speech_key
   AZURE_SPEECH_REGION=your_azure_region
   ```

5. **Start the backend server**:
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   
   The application will be available at `http://localhost:5173`

## 📱 Usage

### Chat Interface
- Type questions about farming, crop diseases, market prices, or government schemes
- Upload images of crop problems for AI analysis
- Get actionable recommendations and local remedies

### Voice Interface
- Click the microphone button to start voice input
- Speak your question in your preferred language
- Listen to AI responses using text-to-speech

### Side Panel
- Access real-time market prices for popular crops
- Browse government schemes and subsidies
- Read farming tips and best practices

## 🎯 Target Users

- **Small-scale farmers** in Karnataka and other Indian states
- **Rural farmers** with limited access to agricultural expertise
- **Young farmers** looking for modern agricultural guidance

## 🌐 Multilingual Support

The application supports multiple languages:
- **English (en)**: Default language
- **Kannada (kn)**: ಕನ್ನಡ - Primary target language for Karnataka farmers
- **Hindi (hi)**: हिन्दी - Widely understood across India
- **Tamil (ta)**: தமிழ் - For Tamil-speaking farmers

---

**AgriMitra** - *Empowering farmers with AI-driven agricultural intelligence*
