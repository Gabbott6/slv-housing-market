"""
Market trend model for tracking housing market statistics over time.
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, Text
from ..database import Base


class MarketTrend(Base):
    """Market trend data model."""

    __tablename__ = "market_trends"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Date and Region
    date = Column(Date, nullable=False, index=True)
    region = Column(String(100), index=True)  # e.g., "Salt Lake County", "Provo"

    # Metric Information
    metric_name = Column(String(100), nullable=False, index=True)
    # Examples:
    # - "median_sale_price"
    # - "inventory_count"
    # - "days_on_market_avg"
    # - "price_per_sqft_avg"
    # - "sales_volume"

    value = Column(Numeric(12, 2), nullable=False)

    # Additional Context
    metric_type = Column(String(50))  # e.g., "price", "volume", "time", "inventory"
    unit = Column(String(50))  # e.g., "USD", "count", "days"

    # Source Information
    source_name = Column(String(100))
    source_url = Column(Text)
    data_quality = Column(String(20))  # e.g., "verified", "estimated", "preliminary"

    def __repr__(self):
        return f"<MarketTrend(date={self.date}, region='{self.region}', metric='{self.metric_name}', value={self.value})>"
