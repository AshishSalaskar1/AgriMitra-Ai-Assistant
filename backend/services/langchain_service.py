from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any, Optional
import json
import logging
from PIL import Image
import base64
import io

from core.config import settings

logger = logging.getLogger(__name__)

class LangChainService:
    def __init__(self):
        # Validate Azure OpenAI configuration
        if not settings.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        if not settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        
        self.chat_model = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_deployment=settings.azure_openai_deployment_name,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Memory for conversation history
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Agricultural knowledge prompts
        self.setup_prompts()
    
    def setup_prompts(self):
        """Setup specialized prompts for agricultural assistance"""
        
        self.system_prompt = """You are AgriMitra, an expert agricultural assistant specifically designed to help farmers in Karnataka, India. 

        Your expertise includes:
        - Crop disease diagnosis and treatment
        - Pest identification and management
        - Market price analysis and selling advice
        - Government agricultural schemes and subsidies
        - Farming best practices for the Karnataka region
        - Local and affordable remedy suggestions

        Guidelines:
        1. Always provide practical, actionable advice
        2. Suggest locally available and affordable solutions
        3. Consider the farmer's economic constraints
        4. Be empathetic and understanding of rural challenges
        5. Use simple, clear language
        6. Provide step-by-step instructions when needed
        7. Include preventive measures
        8. Support multiple languages (English and Kannada)

        When analyzing crop images:
        - Identify the crop type first
        - Look for signs of disease, pest damage, or nutrient deficiency
        - Provide confidence levels in your diagnosis
        - Suggest immediate and long-term solutions
        - Recommend local treatment options
        - Consider the stage of crop growth
        - Mention weather conditions that might have contributed
        """
        
        self.image_analysis_prompt = """Analyze this crop image as an expert agricultural consultant. Please provide a detailed analysis including:

        1. **Crop Identification**: What type of crop is this?
        2. **Health Assessment**: Overall health status of the plant
        3. **Disease/Pest Identification**: Any visible diseases, pests, or issues
        4. **Severity Level**: How serious is the problem (mild/moderate/severe)
        5. **Confidence Level**: Your confidence in the diagnosis (0-100%)
        6. **Immediate Actions**: What the farmer should do right now
        7. **Treatment Options**: 
           - Organic/natural remedies available locally
           - Chemical treatments if necessary
           - Preventive measures
        8. **Timeline**: Expected recovery time and monitoring schedule
        9. **Cost Considerations**: Approximate costs for treatments
        10. **Prevention**: How to prevent this issue in future

        Focus on practical, affordable solutions available to small-scale farmers in rural Karnataka.
        If you're unsure about something, mention it clearly.
        """

    async def process_chat_message(self, message: str, conversation_history: List[Dict], language: str = "en") -> Dict[str, Any]:
        """Process a general chat message with agricultural context"""
        try:
            # Prepare conversation context
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add conversation history
            for msg in conversation_history[-5:]:  # Keep last 5 messages for context
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current message
            if language == "kn":
                message = f"[Please respond in Kannada language] {message}"
            
            messages.append(HumanMessage(content=message))
            
            # Get response from Azure OpenAI
            response = await self.chat_model.ainvoke(messages)
            
            # Analyze message type and provide suggestions
            suggested_actions = self._get_suggested_actions(message)
            
            return {
                "response": response.content,
                "conversation_id": "default",  # Could implement UUID-based sessions
                "suggested_actions": suggested_actions
            }
            
        except Exception as e:
            logger.error(f"Error in LangChain chat processing: {str(e)}")
            raise e

    async def analyze_crop_image(self, image: Image.Image, query: str = "", language: str = "en") -> Dict[str, Any]:
        """Analyze crop image using GPT-4o multimodal capabilities"""
        try:
            # Convert image to base64 for GPT-4o
            buffer = io.BytesIO()
            # Optimize image size for better API performance
            if image.size[0] > 1024 or image.size[1] > 1024:
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            image.save(buffer, format="JPEG", quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Prepare multimodal prompt
            analysis_prompt = f"{self.image_analysis_prompt}\n\nUser Query: {query}" if query else self.image_analysis_prompt
            
            if language == "kn":
                analysis_prompt = f"[Please respond in Kannada language] {analysis_prompt}"
            
            # Create message with image and text for GPT-4o
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=[
                    {
                        "type": "text", 
                        "text": analysis_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"  # Use high detail for better crop analysis
                        }
                    }
                ])
            ]
            
            # Get response from GPT-4o
            response = await self.chat_model.ainvoke(messages)
            
            # Parse response and extract structured information
            analysis_result = self._parse_image_analysis(response.content)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in crop image analysis: {str(e)}")
            # Fallback response
            return {
                "analysis": f"I'm having trouble analyzing the image right now. Error: {str(e)}. Please try uploading a clearer image or describe the issue you're seeing with your crops.",
                "disease_detected": None,
                "confidence_score": 0.0,
                "recommended_actions": ["Upload a clearer image", "Describe the problem in text", "Check image size and quality"],
                "local_remedies": []
            }

    def _get_suggested_actions(self, message: str) -> List[str]:
        """Generate contextual action suggestions based on message content"""
        message_lower = message.lower()
        suggestions = []
        
        if any(word in message_lower for word in ["disease", "spot", "yellow", "brown", "pest", "bug", "insect"]):
            suggestions.extend([
                "Upload an image of the affected plant",
                "Check market prices for your crop",
                "Look for organic treatment options"
            ])
        elif any(word in message_lower for word in ["price", "sell", "market", "mandi"]):
            suggestions.extend([
                "Check current market prices",
                "Find nearby mandis",
                "Look for government schemes"
            ])
        elif any(word in message_lower for word in ["subsidy", "scheme", "government", "loan"]):
            suggestions.extend([
                "Search government schemes",
                "Check eligibility criteria",
                "Find application procedures"
            ])
        elif any(word in message_lower for word in ["weather", "rain", "drought", "irrigation"]):
            suggestions.extend([
                "Check weather forecasts",
                "Look for drought-resistant varieties",
                "Explore irrigation subsidies"
            ])
        else:
            suggestions.extend([
                "Upload crop images for analysis",
                "Check market prices",
                "Explore government schemes"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions

    def _parse_image_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response to extract structured information"""
        try:
            # Extract structured information from the response
            analysis_result = {
                "analysis": response_text,
                "disease_detected": None,
                "confidence_score": None,
                "recommended_actions": [],
                "local_remedies": []
            }
            
            # Simple keyword extraction for disease detection
            response_lower = response_text.lower()
            
            # Common crop diseases in Karnataka
            diseases = [
                "blight", "wilt", "rust", "mildew", "mosaic", "rot", "canker", 
                "anthracnose", "leaf spot", "powdery mildew", "downy mildew",
                "bacterial", "fungal", "viral", "aphid", "thrips", "whitefly"
            ]
            
            for disease in diseases:
                if disease in response_lower:
                    analysis_result["disease_detected"] = disease.title()
                    break
            
            # Extract confidence percentage
            import re
            confidence_patterns = [
                r'confidence[:\s]*(\d+)%',
                r'(\d+)%\s*confidence',
                r'confidence[:\s]*(\d+)',
                r'(\d+)\s*percent'
            ]
            
            for pattern in confidence_patterns:
                confidence_match = re.search(pattern, response_text, re.IGNORECASE)
                if confidence_match:
                    analysis_result["confidence_score"] = float(confidence_match.group(1)) / 100
                    break
            
            # Extract actionable items and remedies
            lines = response_text.split('\n')
            actions = []
            remedies = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for action items
                if any(word in line.lower() for word in [
                    "spray", "apply", "use", "treat", "remove", "cut", "water", 
                    "fertilize", "prune", "harvest", "isolate"
                ]):
                    if any(word in line.lower() for word in [
                        "neem", "organic", "local", "traditional", "natural", 
                        "turmeric", "garlic", "soap", "ash"
                    ]):
                        remedies.append(line.strip())
                    else:
                        actions.append(line.strip())
                
                # Look for numbered lists
                elif re.match(r'^\d+\.', line) and len(line) > 10:
                    if any(word in line.lower() for word in ["neem", "organic", "local"]):
                        remedies.append(line.strip())
                    else:
                        actions.append(line.strip())
            
            analysis_result["recommended_actions"] = actions[:5]  # Top 5 actions
            analysis_result["local_remedies"] = remedies[:3]      # Top 3 remedies
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error parsing image analysis: {str(e)}")
            return {
                "analysis": response_text,
                "disease_detected": None,
                "confidence_score": None,
                "recommended_actions": [],
                "local_remedies": []
            }
