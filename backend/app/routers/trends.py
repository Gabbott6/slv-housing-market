"""
Market Trends API router.
Handles market statistics and historical data.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, timedelta

from ..database import get_db
from ..models.market_trend import MarketTrend


router = APIRouter()


# Pydantic schemas
class TrendResponse(BaseModel):
    id: int
    date: date
    region: str
    metric_name: str
    value: float
    metric_type: Optional[str]
    unit: Optional[str]
    source_name: Optional[str]

    class Config:
        from_attributes = True


class TrendSummary(BaseModel):
    metric_name: str
    region: str
    current_value: float
    previous_value: Optional[float]
    change_percent: Optional[float]
    data_points: int


@router.get("/", response_model=List[TrendResponse])
async def get_trends(
    region: Optional[str] = Query(None, description="Region filter"),
    metric_name: Optional[str] = Query(None, description="Metric name filter"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get market trend data with optional filters.

    Common metrics:
    - median_sale_price
    - inventory_count
    - days_on_market_avg
    - price_per_sqft_avg
    - sales_volume
    """
    query = db.query(MarketTrend)

    # Apply filters
    if region:
        query = query.filter(MarketTrend.region.ilike(f"%{region}%"))
    if metric_name:
        query = query.filter(MarketTrend.metric_name == metric_name)
    if start_date:
        query = query.filter(MarketTrend.date >= start_date)
    if end_date:
        query = query.filter(MarketTrend.date <= end_date)

    # Order by date descending
    query = query.order_by(MarketTrend.date.desc())

    trends = query.limit(limit).all()
    return trends


@router.get("/summary", response_model=List[TrendSummary])
async def get_trend_summary(
    region: str = Query("Salt Lake County", description="Region"),
    db: Session = Depends(get_db)
):
    """
    Get summary of current trends with comparison to previous period.
    """
    # Get unique metrics for the region
    metrics = db.query(MarketTrend.metric_name).filter(
        MarketTrend.region == region
    ).distinct().all()

    summaries = []

    for (metric_name,) in metrics:
        # Get most recent value
        current = db.query(MarketTrend).filter(
            MarketTrend.region == region,
            MarketTrend.metric_name == metric_name
        ).order_by(MarketTrend.date.desc()).first()

        if not current:
            continue

        # Get previous value (30 days earlier)
        previous_date = current.date - timedelta(days=30)
        previous = db.query(MarketTrend).filter(
            MarketTrend.region == region,
            MarketTrend.metric_name == metric_name,
            MarketTrend.date <= previous_date
        ).order_by(MarketTrend.date.desc()).first()

        # Calculate change
        change_percent = None
        if previous and previous.value != 0:
            change_percent = ((float(current.value) - float(previous.value)) / float(previous.value)) * 100

        # Count data points
        data_points = db.query(func.count(MarketTrend.id)).filter(
            MarketTrend.region == region,
            MarketTrend.metric_name == metric_name
        ).scalar()

        summaries.append(TrendSummary(
            metric_name=metric_name,
            region=region,
            current_value=float(current.value),
            previous_value=float(previous.value) if previous else None,
            change_percent=round(change_percent, 2) if change_percent else None,
            data_points=data_points
        ))

    return summaries


@router.post("/")
async def add_trend_data(
    trend_data: List[dict],
    db: Session = Depends(get_db)
):
    """
    Add market trend data (batch insert).

    Expected format:
    [
        {
            "date": "2024-01-01",
            "region": "Salt Lake County",
            "metric_name": "median_sale_price",
            "value": 525000.00,
            "metric_type": "price",
            "unit": "USD",
            "source_name": "Redfin Data Center"
        }
    ]
    """
    try:
        count = 0
        for item in trend_data:
            trend = MarketTrend(
                date=datetime.strptime(item["date"], "%Y-%m-%d").date(),
                region=item["region"],
                metric_name=item["metric_name"],
                value=float(item["value"]),
                metric_type=item.get("metric_type"),
                unit=item.get("unit"),
                source_name=item.get("source_name"),
                source_url=item.get("source_url")
            )
            db.add(trend)
            count += 1

        db.commit()

        return {
            "message": f"Successfully added {count} trend data points",
            "count": count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add trends: {str(e)}")
