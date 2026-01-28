"""
Property AI API Router.
Handles AI-powered property analysis endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from ..database import get_db
from ..services.property_analysis_service import PropertyAnalysisService


router = APIRouter()


# Request/Response Models
class PropertyFilters(BaseModel):
    """Filters for property queries."""
    price_min: Optional[float] = Field(None, description="Minimum price")
    price_max: Optional[float] = Field(None, description="Maximum price")
    beds: Optional[int] = Field(None, description="Minimum bedrooms")
    baths: Optional[float] = Field(None, description="Minimum bathrooms")
    city: Optional[str] = Field(None, description="City name")


class PropertySummaryRequest(BaseModel):
    """Request model for property summary."""
    filters: Optional[PropertyFilters] = Field(None, description="Property filters")
    max_properties: int = Field(50, ge=1, le=100, description="Maximum properties to analyze")
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Areas to focus on (e.g., 'best_value', 'family_friendly')"
    )


class BuyerRecommendations(BaseModel):
    """Recommendations by buyer type."""
    first_time_buyer: Optional[str] = None
    family: Optional[str] = None
    investor: Optional[str] = None


class PropertySummaryResponse(BaseModel):
    """Response model for property summary."""
    summary: str = Field(..., description="Overall market summary")
    key_insights: List[str] = Field(default_factory=list, description="Key insights")
    buyer_recommendations: BuyerRecommendations = Field(
        default_factory=BuyerRecommendations,
        description="Recommendations by buyer type"
    )
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Market statistics")
    properties_analyzed: int = Field(..., description="Number of properties analyzed")
    confidence: str = Field(..., description="Confidence level (low/medium/high)")
    from_cache: bool = Field(False, description="Whether response came from cache")
    error: Optional[str] = Field(None, description="Error message if any")


class RecommendationCriteria(BaseModel):
    """Criteria for property recommendations."""
    budget_max: float = Field(..., description="Maximum budget")
    beds_min: Optional[int] = Field(None, description="Minimum bedrooms")
    baths_min: Optional[float] = Field(None, description="Minimum bathrooms")
    priorities: Optional[Dict[str, int]] = Field(
        None,
        description="Priority weights (monthly_cost, location, value, space)"
    )
    lifestyle: Optional[str] = Field(
        None,
        description="Lifestyle (first_time_buyer, family, investor, downsizer)"
    )
    city_preference: Optional[str] = Field(None, description="Preferred city")


class PropertyRecommendation(BaseModel):
    """Single property recommendation."""
    property_id: int = Field(..., description="Property ID")
    address: str = Field(..., description="Property address")
    city: Optional[str] = Field(None, description="City")
    price: float = Field(..., description="Property price")
    match_score: float = Field(..., description="Match score (0-100)")
    match_explanation: str = Field(..., description="Why this property matches")
    pros: List[str] = Field(default_factory=list, description="Advantages")
    cons: List[str] = Field(default_factory=list, description="Concerns")


class PropertyRecommendationResponse(BaseModel):
    """Response model for property recommendations."""
    message: str = Field(..., description="Response message")
    recommended_properties: List[int] = Field(
        default_factory=list,
        description="Property IDs of recommendations"
    )
    recommendations: List[PropertyRecommendation] = Field(
        default_factory=list,
        description="Detailed recommendations"
    )
    confidence: str = Field("medium", description="Confidence level (low/medium/high)")
    from_cache: bool = Field(False, description="Whether from cache")
    error: Optional[str] = Field(None, description="Error message if any")


class PropertyComparisonRequest(BaseModel):
    """Request model for property comparison."""
    property_ids: List[int] = Field(..., min_items=2, max_items=5, description="Property IDs to compare")
    aspects: Optional[List[str]] = Field(
        None,
        description="Aspects to compare (price, value, space, location)"
    )


class WinnerInfo(BaseModel):
    """Winner information for a category."""
    property_letter: str = Field(..., description="Property letter (A, B, C, etc.)")
    reason: str = Field(..., description="Reason why this property wins")


class PropertyDetail(BaseModel):
    """Property detail for comparison."""
    property_id: int
    property_letter: str
    address: str
    city: Optional[str]
    price: float
    monthly_cost: Optional[float]
    sqft: Optional[int]
    price_per_sqft: Optional[float]


class PropertyComparisonResponse(BaseModel):
    """Response model for property comparison."""
    summary: str = Field(..., description="Comparison summary")
    winners: Dict[str, WinnerInfo] = Field(
        default_factory=dict,
        description="Winners by category"
    )
    overall_recommendation: WinnerInfo = Field(..., description="Overall recommendation")
    properties: List[PropertyDetail] = Field(
        default_factory=list,
        description="Property details"
    )
    confidence: str = Field("medium", description="Confidence level")
    from_cache: bool = Field(False, description="Whether from cache")
    error: Optional[str] = Field(None, description="Error message if any")


class MarketAnalysisRequest(BaseModel):
    """Request model for market analysis."""
    region: Optional[str] = Field(None, description="Region/city to analyze")
    time_period: Optional[str] = Field("30d", description="Time period (7d, 30d, 90d)")
    focus: Optional[str] = Field(None, description="Analysis focus area")


class MarketAnalysisResponse(BaseModel):
    """Response model for market analysis."""
    analysis: str = Field(..., description="Market analysis summary")
    trends: List[str] = Field(default_factory=list, description="Market trends")
    buyer_opportunities: Optional[str] = Field(None, description="Opportunities for buyers")
    seller_considerations: Optional[str] = Field(None, description="Considerations for sellers")
    price_outlook: Optional[str] = Field(None, description="Price predictions")
    statistics: Optional[Dict[str, Any]] = Field(None, description="Market statistics")
    market_temperature: Optional[str] = Field(None, description="Market temperature (hot/warm/cool/cold)")
    dom_distribution: Optional[Dict[str, Any]] = Field(None, description="Days on market distribution")
    confidence: str = Field("medium", description="Confidence level")
    from_cache: bool = Field(False, description="Whether result is from cache")
    error: Optional[str] = Field(None, description="Error message if any")


# Endpoints
@router.post("/summarize", response_model=PropertySummaryResponse)
async def summarize_properties(
    request: PropertySummaryRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered summary of properties matching filters.

    Analyzes properties and provides:
    - Overall market summary
    - Key insights and trends
    - Recommendations by buyer type
    - Market statistics
    """
    try:
        # Initialize service
        service = PropertyAnalysisService(db)

        # Convert filters to dict
        filters_dict = request.filters.dict() if request.filters else None

        # Get summary
        result = await service.summarize_properties(
            filters=filters_dict,
            max_properties=request.max_properties
        )

        # Convert to response model
        return PropertySummaryResponse(
            summary=result["summary"],
            key_insights=result.get("key_insights", []),
            buyer_recommendations=BuyerRecommendations(
                **result.get("buyer_recommendations", {})
            ),
            statistics=result.get("statistics", {}),
            properties_analyzed=result.get("properties_analyzed", 0),
            confidence=result.get("confidence", "low"),
            from_cache=result.get("from_cache", False),
            error=result.get("error")
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.post("/recommend", response_model=PropertyRecommendationResponse)
async def recommend_properties(
    request: RecommendationCriteria,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered property recommendations based on buyer criteria.

    Analyzes properties and provides:
    - Match scores (0-100) based on criteria
    - Personalized explanations
    - Pros and cons for each recommendation
    """
    try:
        # Initialize service
        service = PropertyAnalysisService(db)

        # Convert criteria to dict
        criteria_dict = request.dict()

        # Get recommendations
        result = await service.recommend_properties(
            criteria=criteria_dict,
            max_recommendations=5
        )

        # Build response
        return PropertyRecommendationResponse(
            message=result.get("message", "Here are your recommendations"),
            recommended_properties=[rec["property_id"] for rec in result.get("recommendations", [])],
            recommendations=result.get("recommendations", []),
            confidence=result.get("confidence", "medium"),
            from_cache=result.get("from_cache", False),
            error=result.get("error")
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.post("/compare", response_model=PropertyComparisonResponse)
async def compare_properties(
    request: PropertyComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    Compare multiple properties with AI insights.

    Analyzes 2-5 properties and provides:
    - Side-by-side comparison
    - Winner identification by category
    - Overall recommendation with reasoning
    """
    try:
        # Validate property count
        if len(request.property_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 properties required for comparison")
        if len(request.property_ids) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 properties can be compared at once")

        # Initialize service
        service = PropertyAnalysisService(db)

        # Get comparison
        result = await service.compare_properties(
            property_ids=request.property_ids,
            aspects=request.aspects
        )

        # Build response
        return PropertyComparisonResponse(
            summary=result.get("summary", ""),
            winners={k: WinnerInfo(**v) for k, v in result.get("winners", {}).items()},
            overall_recommendation=WinnerInfo(**result.get("overall_recommendation", {
                "property_letter": "A",
                "reason": "Based on overall comparison"
            })),
            properties=[PropertyDetail(**p) for p in result.get("properties", [])],
            confidence=result.get("confidence", "medium"),
            from_cache=result.get("from_cache", False),
            error=result.get("error")
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def analyze_market(
    request: MarketAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered market analysis for a region.

    Provides:
    - Overall market summary and trends
    - Buyer opportunities and seller considerations
    - Price outlook and predictions
    - Market temperature analysis
    - Days on market distribution
    """
    try:
        # Initialize service
        service = PropertyAnalysisService(db)

        # Get market analysis
        result = await service.analyze_market_trends(
            region=request.region,
            time_period=request.time_period or "30d",
            focus=request.focus
        )

        # Build response
        return MarketAnalysisResponse(
            analysis=result.get("analysis", ""),
            trends=result.get("trends", []),
            buyer_opportunities=result.get("buyer_opportunities"),
            seller_considerations=result.get("seller_considerations"),
            price_outlook=result.get("price_outlook"),
            statistics=result.get("statistics"),
            market_temperature=result.get("market_temperature"),
            dom_distribution=result.get("dom_distribution"),
            confidence=result.get("confidence", "medium"),
            from_cache=result.get("from_cache", False),
            error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for AI service."""
    return {
        "status": "healthy",
        "service": "Property AI Analysis",
        "phase": "1 (Property Summaries)"
    }
