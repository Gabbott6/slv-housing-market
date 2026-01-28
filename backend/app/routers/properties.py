"""
Properties API router.
Handles property listings, filtering, sorting, and CSV uploads.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
import tempfile
import os

from ..database import get_db
from ..models.property import Property
from ..services.data_sources.manual_upload import ManualUploadDataSource
from ..services.calculator import get_cost_breakdown
from ..services.property_scraper import PropertyScraperService


router = APIRouter()


# Pydantic schemas for request/response
class PropertyResponse(BaseModel):
    id: int
    address: str
    city: Optional[str]
    price: float
    beds: Optional[int]
    baths: Optional[float]
    sqft: Optional[int]
    price_per_sqft: Optional[float]
    property_type: Optional[str]
    hoa_fee: Optional[float]

    # Calculated costs
    monthly_mortgage: Optional[float]
    monthly_taxes: Optional[float]
    monthly_insurance: Optional[float]
    monthly_hoa: Optional[float]
    total_monthly_cost: Optional[float]

    # Listing info
    days_on_market: Optional[int]
    listing_url: Optional[str]
    seller_score: Optional[float]

    # Sources
    price_source_name: Optional[str]
    price_source_url: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PropertyResponse])
async def get_properties(
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    beds: Optional[int] = Query(None, description="Minimum bedrooms"),
    baths: Optional[float] = Query(None, description="Minimum bathrooms"),
    city: Optional[str] = Query(None, description="City filter"),
    sort_by: str = Query("total_monthly_cost", description="Sort field"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
    limit: int = Query(100, le=500, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Get property listings with filtering and sorting.

    Sort options:
    - total_monthly_cost: Best monthly cost
    - price: Best overall price
    - seller_score: Best seller rating
    - price_per_sqft: Best value per square foot
    """
    query = db.query(Property)

    # Apply filters
    if price_min is not None:
        query = query.filter(Property.price >= price_min)
    if price_max is not None:
        query = query.filter(Property.price <= price_max)
    if beds is not None:
        query = query.filter(Property.beds >= beds)
    if baths is not None:
        query = query.filter(Property.baths >= baths)
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))

    # Apply sorting
    valid_sort_fields = {
        "total_monthly_cost": Property.total_monthly_cost,
        "price": Property.price,
        "seller_score": Property.seller_score,
        "price_per_sqft": Property.price_per_sqft,
        "days_on_market": Property.days_on_market
    }

    sort_field = valid_sort_fields.get(sort_by, Property.total_monthly_cost)

    if sort_order == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    # Execute query
    properties = query.limit(limit).all()

    return properties


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific property by ID."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    return property_obj


@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload properties via CSV file.

    Expected CSV columns:
    - address (required)
    - city
    - price (required)
    - beds
    - baths
    - sqft
    - property_type
    - hoa_fee
    - listing_url
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Upload using data source
        data_source = ManualUploadDataSource(db)
        count = await data_source.upload_csv(tmp_path)

        # Clean up temp file
        os.unlink(tmp_path)

        return {
            "message": f"Successfully uploaded {count} properties",
            "count": count
        }

    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{property_id}/costs")
async def get_property_costs(
    property_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed cost breakdown for a property."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    costs = get_cost_breakdown(property_obj)

    return {
        "property_id": property_id,
        "address": property_obj.address,
        "costs": costs
    }


@router.delete("/{property_id}")
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """Delete a property (admin function)."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    db.delete(property_obj)
    db.commit()

    return {"message": "Property deleted successfully"}


class QuickAddPropertyRequest(BaseModel):
    """Request model for quick-add property."""
    address: str
    city: Optional[str] = None
    price: float
    beds: Optional[int] = None
    baths: Optional[float] = None
    sqft: Optional[int] = None
    hoa_fee: Optional[float] = None
    listing_url: Optional[str] = None
    notes: Optional[str] = None


class ImportFromUrlRequest(BaseModel):
    """Request model for importing property from URL."""
    url: str


@router.post("/quick-add", response_model=PropertyResponse)
async def quick_add_property(
    request: QuickAddPropertyRequest,
    db: Session = Depends(get_db)
):
    """
    Quick-add a property with minimal data entry.

    Automatically calculates monthly costs and price per sqft.
    Perfect for manually copying properties from Zillow/Redfin.
    """
    try:
        # Create property object
        new_property = Property(
            address=request.address,
            city=request.city or "Salt Lake City",
            price=Decimal(str(request.price)),
            beds=request.beds,
            baths=request.baths,
            sqft=request.sqft,
            hoa_fee=Decimal(str(request.hoa_fee)) if request.hoa_fee else None,
            listing_url=request.listing_url,
            property_type="Single Family",  # Default
            data_source="manual_quick_add"
        )

        # Calculate price per sqft if possible
        if request.sqft and request.sqft > 0:
            new_property.price_per_sqft = Decimal(str(request.price)) / Decimal(str(request.sqft))

        # Save to database
        db.add(new_property)
        db.commit()
        db.refresh(new_property)

        # Calculate monthly costs using the calculator service
        costs = get_cost_breakdown(new_property)

        # Update property with calculated costs
        new_property.monthly_mortgage = Decimal(str(costs["monthly_mortgage"]))
        new_property.monthly_taxes = Decimal(str(costs["monthly_taxes"]))
        new_property.monthly_insurance = Decimal(str(costs["monthly_insurance"]))
        new_property.monthly_hoa = Decimal(str(costs.get("monthly_hoa", 0)))
        new_property.total_monthly_cost = Decimal(str(costs["total_monthly_cost"]))

        db.commit()
        db.refresh(new_property)

        return PropertyResponse.from_orm(new_property)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add property: {str(e)}")


@router.post("/import-from-url")
async def import_property_from_url(request: ImportFromUrlRequest):
    """
    Import property data from a Zillow or Redfin URL.

    This endpoint scrapes property information from the provided URL
    and returns the extracted data without saving it to the database.
    The frontend can then preview and confirm before saving.
    """
    try:
        scraper = PropertyScraperService()
        property_data = scraper.scrape_property(request.url)

        return {
            "success": True,
            "data": property_data,
            "message": "Property data extracted successfully"
        }

    except ValueError as e:
        # Scraping-specific errors (invalid URL, unsupported site, etc.)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # General errors
        raise HTTPException(status_code=500, detail=f"Failed to extract property data: {str(e)}")
