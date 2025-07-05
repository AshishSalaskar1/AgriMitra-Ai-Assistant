from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import requests
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

class MarketPriceRequest(BaseModel):
    crop_name: str
    location: Optional[str] = "Karnataka"
    language: Optional[str] = "en"

class MarketPriceResponse(BaseModel):
    crop_name: str
    current_price: float
    price_unit: str
    market_name: str
    price_date: str
    trend: str  # "increasing", "decreasing", "stable"
    trend_percentage: Optional[float] = None
    recommendations: List[str] = []

class MarketTrendResponse(BaseModel):
    crop_name: str
    historical_prices: List[Dict] = []
    forecast: List[Dict] = []
    best_selling_time: str
    market_insights: List[str] = []

class MockMarketService:
    """Mock market data service for development"""
    
    def __init__(self):
        # Mock data for common crops in Karnataka
        self.mock_prices = {
            "tomato": {
                "current_price": 25.50,
                "unit": "per kg",
                "trend": "increasing",
                "trend_percentage": 12.5,
                "market": "Bangalore APMC"
            },
            "onion": {
                "current_price": 18.75,
                "unit": "per kg", 
                "trend": "stable",
                "trend_percentage": 2.1,
                "market": "Mysore Mandi"
            },
            "potato": {
                "current_price": 22.00,
                "unit": "per kg",
                "trend": "decreasing",
                "trend_percentage": -5.3,
                "market": "Hassan Market"
            },
            "rice": {
                "current_price": 45.00,
                "unit": "per kg",
                "trend": "stable",
                "trend_percentage": 1.2,
                "market": "Shimoga APMC"
            },
            "sugarcane": {
                "current_price": 2800.00,
                "unit": "per ton",
                "trend": "increasing",
                "trend_percentage": 8.7,
                "market": "Mandya Sugar Factory"
            }
        }
    
    async def get_current_price(self, crop_name: str, location: str = "Karnataka") -> Dict:
        """Get current market price for a crop"""
        crop_lower = crop_name.lower()
        
        if crop_lower in self.mock_prices:
            data = self.mock_prices[crop_lower]
            return {
                "crop_name": crop_name,
                "current_price": data["current_price"],
                "price_unit": data["unit"],
                "market_name": data["market"],
                "price_date": datetime.now().strftime("%Y-%m-%d"),
                "trend": data["trend"],
                "trend_percentage": data["trend_percentage"],
                "recommendations": self._generate_recommendations(data)
            }
        else:
            # Generate mock data for unknown crops
            import random
            price = round(random.uniform(15.0, 50.0), 2)
            trends = ["increasing", "decreasing", "stable"]
            trend = random.choice(trends)
            
            return {
                "crop_name": crop_name,
                "current_price": price,
                "price_unit": "per kg",
                "market_name": f"{location} Local Market",
                "price_date": datetime.now().strftime("%Y-%m-%d"),
                "trend": trend,
                "trend_percentage": round(random.uniform(-10.0, 15.0), 1),
                "recommendations": [
                    "Monitor price trends for next few days",
                    "Consider nearby markets for better rates",
                    "Check quality requirements before selling"
                ]
            }
    
    def _generate_recommendations(self, price_data: Dict) -> List[str]:
        """Generate selling recommendations based on price data"""
        recommendations = []
        
        if price_data["trend"] == "increasing":
            recommendations.extend([
                "Good time to sell - prices are rising",
                "Consider holding for 2-3 days if possible",
                "Ensure proper storage to maintain quality"
            ])
        elif price_data["trend"] == "decreasing":
            recommendations.extend([
                "Consider selling immediately",
                "Avoid holding stock for too long",
                "Look for alternative markets with better rates"
            ])
        else:  # stable
            recommendations.extend([
                "Prices are stable - good time to sell",
                "Focus on quality to get better rates",
                "Compare prices across different markets"
            ])
        
        return recommendations
    
    async def get_market_trends(self, crop_name: str, days: int = 7) -> Dict:
        """Get historical trends and forecast"""
        import random
        from datetime import datetime, timedelta
        
        # Generate mock historical data
        historical_prices = []
        base_price = self.mock_prices.get(crop_name.lower(), {"current_price": 25.0})["current_price"]
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            price_variation = random.uniform(-3, 3)
            price = round(base_price + price_variation, 2)
            historical_prices.append({
                "date": date,
                "price": price,
                "market": "Local APMC"
            })
        
        # Generate forecast
        forecast = []
        for i in range(1, 4):  # Next 3 days
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            price_variation = random.uniform(-2, 4)
            price = round(base_price + price_variation, 2)
            forecast.append({
                "date": date,
                "predicted_price": price,
                "confidence": random.uniform(0.7, 0.95)
            })
        
        return {
            "crop_name": crop_name,
            "historical_prices": historical_prices,
            "forecast": forecast,
            "best_selling_time": "Within next 2-3 days",
            "market_insights": [
                f"Average price over {days} days: ₹{round(sum(p['price'] for p in historical_prices)/len(historical_prices), 2)}",
                "Demand is seasonal - festival season shows higher prices",
                "Transportation costs affect final margins",
                "Quality grading significantly impacts price"
            ]
        }

# Initialize service
market_service = MockMarketService()

@router.get("/price/{crop_name}", response_model=MarketPriceResponse)
async def get_crop_price(crop_name: str, location: str = "Karnataka"):
    """Get current market price for a crop"""
    try:
        logger.info(f"Getting price for crop: {crop_name} in {location}")
        
        price_data = await market_service.get_current_price(crop_name, location)
        
        return MarketPriceResponse(**price_data)
        
    except Exception as e:
        logger.error(f"Error getting crop price: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch price data: {str(e)}")

@router.get("/trends/{crop_name}", response_model=MarketTrendResponse)
async def get_market_trends(crop_name: str, days: int = 7):
    """Get market trends and forecast for a crop"""
    try:
        logger.info(f"Getting market trends for: {crop_name}")
        
        trend_data = await market_service.get_market_trends(crop_name, days)
        
        return MarketTrendResponse(**trend_data)
        
    except Exception as e:
        logger.error(f"Error getting market trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trend data: {str(e)}")

@router.get("/popular-crops")
async def get_popular_crops():
    """Get list of popular crops with current prices"""
    try:
        popular_crops = ["tomato", "onion", "potato", "rice", "sugarcane"]
        crops_data = []
        
        for crop in popular_crops:
            price_data = await market_service.get_current_price(crop)
            crops_data.append({
                "name": crop.title(),
                "price": price_data["current_price"],
                "unit": price_data["price_unit"],
                "trend": price_data["trend"]
            })
        
        return {"popular_crops": crops_data}
        
    except Exception as e:
        logger.error(f"Error getting popular crops: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch crops data: {str(e)}")

@router.post("/analyze-selling-decision")
async def analyze_selling_decision(request: MarketPriceRequest):
    """Get AI-powered selling decision analysis"""
    try:
        # Get market data
        price_data = await market_service.get_current_price(request.crop_name, request.location)
        trend_data = await market_service.get_market_trends(request.crop_name)
        
        # Simple analysis logic (could be enhanced with ML)
        decision = "hold"
        confidence = 0.7
        reasons = []
        
        if price_data["trend"] == "increasing" and price_data["trend_percentage"] > 5:
            decision = "hold"
            reasons.append("Prices are rising significantly")
        elif price_data["trend"] == "decreasing" and price_data["trend_percentage"] < -3:
            decision = "sell"
            reasons.append("Prices are falling, sell to avoid losses")
        else:
            decision = "sell"
            reasons.append("Stable prices, good time to sell")
        
        return {
            "crop_name": request.crop_name,
            "decision": decision,
            "confidence": confidence,
            "current_price": price_data["current_price"],
            "reasons": reasons,
            "recommendations": price_data["recommendations"]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing selling decision: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze selling decision: {str(e)}")
