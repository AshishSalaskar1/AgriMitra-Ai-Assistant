from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SchemeSearchRequest(BaseModel):
    query: str
    state: Optional[str] = "Karnataka"
    category: Optional[str] = None  # "subsidy", "loan", "insurance", "training"
    language: Optional[str] = "en"

class GovernmentScheme(BaseModel):
    name: str
    description: str
    category: str
    eligibility: List[str]
    benefits: List[str]
    application_process: List[str]
    documents_required: List[str]
    application_link: Optional[str] = None
    deadline: Optional[str] = None
    contact_info: Dict = {}

class SchemeSearchResponse(BaseModel):
    schemes: List[GovernmentScheme]
    total_found: int
    search_suggestions: List[str] = []

class MockGovernmentSchemeService:
    """Mock government schemes service for development"""
    
    def __init__(self):
        self.schemes_database = [
            {
                "name": "PM-KISAN Samman Nidhi",
                "description": "Direct income support to farmers providing ₹6000 per year in three equal installments",
                "category": "subsidy",
                "eligibility": [
                    "Small and marginal farmers",
                    "Land holding up to 2 hectares",
                    "Valid Aadhaar card required",
                    "Bank account linked with Aadhaar"
                ],
                "benefits": [
                    "₹2000 per installment (3 times a year)",
                    "Direct bank transfer",
                    "No paperwork after initial registration"
                ],
                "application_process": [
                    "Visit nearest Common Service Center (CSC)",
                    "Provide land documents and Aadhaar",
                    "Fill PM-KISAN application form",
                    "Submit documents for verification",
                    "Receive confirmation SMS"
                ],
                "documents_required": [
                    "Aadhaar Card",
                    "Bank Account Details",
                    "Land Ownership Documents",
                    "Mobile Number"
                ],
                "application_link": "https://pmkisan.gov.in",
                "deadline": "Open throughout the year",
                "contact_info": {
                    "helpline": "155261",
                    "email": "pmkisan-ict@gov.in"
                }
            },
            {
                "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "description": "Crop insurance scheme providing financial support in case of crop loss due to natural calamities",
                "category": "insurance",
                "eligibility": [
                    "All farmers (sharecroppers and tenant farmers included)",
                    "Must have insurable interest in the crop",
                    "Should be growing notified crops in notified areas"
                ],
                "benefits": [
                    "Low premium rates (2% for Kharif, 1.5% for Rabi)",
                    "Coverage for yield losses",
                    "Quick settlement of claims",
                    "Technology-based damage assessment"
                ],
                "application_process": [
                    "Approach nearest bank or insurance company",
                    "Fill crop insurance application",
                    "Pay premium amount",
                    "Receive insurance certificate",
                    "Report crop loss within 72 hours if occurs"
                ],
                "documents_required": [
                    "Aadhaar Card",
                    "Bank Account Details",
                    "Land Records",
                    "Crop Sowing Certificate"
                ],
                "application_link": "https://pmfby.gov.in",
                "deadline": "Usually 1 month before harvest",
                "contact_info": {
                    "helpline": "14434",
                    "email": "support@pmfby.gov.in"
                }
            },
            {
                "name": "Kisan Credit Card (KCC)",
                "description": "Easy access to credit for farmers to meet their production and consumption needs",
                "category": "loan",
                "eligibility": [
                    "All farmers (individual/joint borrowers)",
                    "Tenant farmers and sharecroppers",
                    "Self Help Group members",
                    "Minimum 18 years age"
                ],
                "benefits": [
                    "Interest rate 7% per annum",
                    "No collateral required up to ₹1.6 lakh",
                    "Flexible repayment options",
                    "Insurance coverage included"
                ],
                "application_process": [
                    "Visit nearest bank branch",
                    "Fill KCC application form",
                    "Submit required documents",
                    "Bank verification process",
                    "Receive KCC within 15 days"
                ],
                "documents_required": [
                    "Identity Proof (Aadhaar/PAN)",
                    "Address Proof",
                    "Land Documents",
                    "Income Proof"
                ],
                "application_link": "https://www.nabard.org/kcc",
                "deadline": "Open throughout the year",
                "contact_info": {
                    "helpline": "1800-180-1111",
                    "website": "nabard.org"
                }
            },
            {
                "name": "Soil Health Card Scheme",
                "description": "Provides soil health information to farmers for appropriate nutrient management",
                "category": "training",
                "eligibility": [
                    "All farmers",
                    "No land size restriction",
                    "Available for all crop types"
                ],
                "benefits": [
                    "Free soil testing",
                    "Nutrient recommendations",
                    "Fertilizer recommendations",
                    "Improved crop productivity"
                ],
                "application_process": [
                    "Contact local agriculture officer",
                    "Register for soil sampling",
                    "Collect soil samples as per guidelines",
                    "Submit samples to testing lab",
                    "Receive soil health card"
                ],
                "documents_required": [
                    "Land ownership documents",
                    "Aadhaar Card",
                    "Survey number details"
                ],
                "application_link": "https://soilhealth.dac.gov.in",
                "deadline": "Open throughout the year",
                "contact_info": {
                    "helpline": "011-23382401",
                    "email": "info@soilhealth.com"
                }
            },
            {
                "name": "Micro Irrigation Subsidy",
                "description": "Financial assistance for drip and sprinkler irrigation systems",
                "category": "subsidy",
                "eligibility": [
                    "All categories of farmers",
                    "Minimum 0.2 hectare land",
                    "Maximum 5 hectare per beneficiary"
                ],
                "benefits": [
                    "55% subsidy for general farmers",
                    "75% subsidy for SC/ST farmers", 
                    "Water conservation",
                    "Increased crop yield"
                ],
                "application_process": [
                    "Apply through horticulture department",
                    "Submit detailed project report",
                    "Technical approval from department",
                    "Installation after approval",
                    "Claim subsidy after completion"
                ],
                "documents_required": [
                    "Land documents",
                    "Aadhaar Card",
                    "Bank account details",
                    "Caste certificate (if applicable)"
                ],
                "application_link": "https://pmksy.gov.in",
                "deadline": "Usually April-May each year",
                "contact_info": {
                    "helpline": "011-23382477",
                    "email": "pmksy@nic.in"
                }
            }
        ]
    
    async def search_schemes(self, query: str, state: str = "Karnataka", category: str = None) -> Dict:
        """Search for relevant government schemes"""
        query_lower = query.lower()
        matching_schemes = []
        
        for scheme in self.schemes_database:
            # Check if query matches scheme content
            searchable_text = f"{scheme['name']} {scheme['description']} {' '.join(scheme['benefits'])}".lower()
            
            # Category filter
            if category and scheme['category'] != category:
                continue
            
            # Text matching
            if any(word in searchable_text for word in query_lower.split()):
                matching_schemes.append(GovernmentScheme(**scheme))
        
        # If no specific matches, return schemes based on common keywords
        if not matching_schemes:
            keyword_mapping = {
                "loan": ["loan"],
                "credit": ["loan"],
                "insurance": ["insurance"],
                "subsidy": ["subsidy"],
                "training": ["training"],
                "irrigation": ["subsidy"],
                "water": ["subsidy"],
                "income": ["subsidy"]
            }
            
            for keyword, categories in keyword_mapping.items():
                if keyword in query_lower:
                    for scheme in self.schemes_database:
                        if scheme['category'] in categories:
                            matching_schemes.append(GovernmentScheme(**scheme))
                    break
        
        # Generate search suggestions
        suggestions = [
            "Crop insurance schemes",
            "Irrigation subsidies",
            "Farmer loans and credit",
            "Soil testing programs",
            "Direct benefit transfer schemes"
        ]
        
        return {
            "schemes": matching_schemes[:5],  # Limit to 5 results
            "total_found": len(matching_schemes),
            "search_suggestions": suggestions
        }

# Initialize service
scheme_service = MockGovernmentSchemeService()

@router.get("/search", response_model=SchemeSearchResponse)
async def search_government_schemes(
    query: str = Query(..., description="Search query for schemes"),
    state: str = Query("Karnataka", description="State name"),
    category: Optional[str] = Query(None, description="Scheme category filter")
):
    """Search for relevant government schemes"""
    try:
        logger.info(f"Searching schemes for query: {query}")
        
        results = await scheme_service.search_schemes(query, state, category)
        
        return SchemeSearchResponse(**results)
        
    except Exception as e:
        logger.error(f"Error searching schemes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search schemes: {str(e)}")

@router.get("/categories")
async def get_scheme_categories():
    """Get available scheme categories"""
    return {
        "categories": [
            {"id": "subsidy", "name": "Subsidies & Financial Aid"},
            {"id": "loan", "name": "Loans & Credit"},
            {"id": "insurance", "name": "Insurance Schemes"},
            {"id": "training", "name": "Training & Development"}
        ]
    }

@router.get("/popular")
async def get_popular_schemes():
    """Get most popular/commonly used schemes"""
    popular_scheme_names = [
        "PM-KISAN Samman Nidhi",
        "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "Kisan Credit Card (KCC)"
    ]
    
    popular_schemes = []
    for scheme_data in scheme_service.schemes_database:
        if scheme_data['name'] in popular_scheme_names:
            popular_schemes.append({
                "name": scheme_data['name'],
                "description": scheme_data['description'],
                "category": scheme_data['category'],
                "application_link": scheme_data.get('application_link')
            })
    
    return {"popular_schemes": popular_schemes}

@router.get("/scheme/{scheme_name}")
async def get_scheme_details(scheme_name: str):
    """Get detailed information about a specific scheme"""
    try:
        for scheme_data in scheme_service.schemes_database:
            if scheme_data['name'].lower() == scheme_name.lower():
                return GovernmentScheme(**scheme_data)
        
        raise HTTPException(status_code=404, detail="Scheme not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheme details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheme details: {str(e)}")
