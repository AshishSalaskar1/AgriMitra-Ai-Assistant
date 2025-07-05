from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List
import base64
import io
from PIL import Image
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    language: Optional[str] = "en"  # Default to English, support "kn" for Kannada

class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    suggested_actions: List[str] = []

class ImageAnalysisRequest(BaseModel):
    image_base64: str
    query: Optional[str] = "Analyze this crop image for diseases or issues"
    language: Optional[str] = "en"

class ImageAnalysisResponse(BaseModel):
    analysis: str
    disease_detected: Optional[str] = None
    confidence_score: Optional[float] = None
    recommended_actions: List[str] = []
    local_remedies: List[str] = []

# Initialize services (lazy loading)
langchain_service = None

def get_langchain_service():
    global langchain_service
    if langchain_service is None:
        from services.langchain_service import LangChainService
        langchain_service = LangChainService()
    return langchain_service

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Process a chat message using LangChain and Azure OpenAI GPT-4o
    """
    try:
        logger.info(f"Processing chat message: {request.message[:50]}...")
        
        # Use LangChain service to process the message
        service = get_langchain_service()
        response = await service.process_chat_message(
            message=request.message,
            conversation_history=[msg.dict() for msg in request.conversation_history],
            language=request.language
        )
        
        return ChatResponse(
            response=response["response"],
            conversation_id=response.get("conversation_id"),
            suggested_actions=response.get("suggested_actions", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_crop_image(request: ImageAnalysisRequest):
    """
    Analyze crop images for disease detection using GPT-4o multimodal capabilities
    """
    try:
        logger.info("Processing crop image analysis with GPT-4o...")
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.image_base64)
            image = Image.open(io.BytesIO(image_data))
        except Exception as img_error:
            logger.error(f"Error decoding image: {str(img_error)}")
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Validate image
        if image.size[0] < 50 or image.size[1] < 50:
            raise HTTPException(status_code=400, detail="Image too small for analysis")
        
        # Use LangChain service for image analysis with GPT-4o
        service = get_langchain_service()
        analysis_result = await service.analyze_crop_image(
            image=image,
            query=request.query,
            language=request.language
        )
        
        return ImageAnalysisResponse(
            analysis=analysis_result["analysis"],
            disease_detected=analysis_result.get("disease_detected"),
            confidence_score=analysis_result.get("confidence_score"),
            recommended_actions=analysis_result.get("recommended_actions", []),
            local_remedies=analysis_result.get("local_remedies", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing crop image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")

@router.post("/upload-image")
async def upload_image_file(file: UploadFile = File(...)):
    """
    Upload an image file and return base64 encoded data for GPT-4o analysis
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file size (limit to 10MB)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        # Validate and optimize image
        try:
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Optimize size for GPT-4o (max 1024x1024 for best performance)
            if image.size[0] > 1024 or image.size[1] > 1024:
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Re-encode optimized image
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85, optimize=True)
            optimized_content = buffer.getvalue()
            
        except Exception as img_error:
            logger.error(f"Error processing image: {str(img_error)}")
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file")
        
        # Encode to base64
        image_base64 = base64.b64encode(optimized_content).decode("utf-8")
        
        return {
            "image_base64": image_base64,
            "filename": file.filename,
            "content_type": "image/jpeg",
            "optimized": True,
            "size": len(optimized_content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
