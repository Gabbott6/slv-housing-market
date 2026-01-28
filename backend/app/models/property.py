"""
Property model for storing real estate listings.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base


class Property(Base):
    """Property listing model."""

    __tablename__ = "properties"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    address = Column(String(255), nullable=False, index=True)
    city = Column(String(100), index=True)
    state = Column(String(2), default="UT")
    zip_code = Column(String(10))

    # Property Details
    price = Column(Numeric(12, 2), nullable=False, index=True)
    beds = Column(Integer)
    baths = Column(Numeric(3, 1))
    sqft = Column(Integer)
    price_per_sqft = Column(Numeric(8, 2))
    property_type = Column(String(50))  # e.g., "Single Family", "Condo", "Townhouse"
    year_built = Column(Integer)
    lot_size = Column(Numeric(10, 2))  # In acres

    # Financial Details
    hoa_fee = Column(Numeric(8, 2), default=0.0)  # Monthly HOA fee
    property_tax = Column(Numeric(10, 2))  # Annual property tax
    tax_rate = Column(Numeric(5, 4))  # Tax rate as decimal (e.g., 0.0056 for 0.56%)

    # Calculated Monthly Costs
    monthly_mortgage = Column(Numeric(10, 2))
    monthly_taxes = Column(Numeric(10, 2))
    monthly_insurance = Column(Numeric(10, 2))
    monthly_hoa = Column(Numeric(10, 2))
    total_monthly_cost = Column(Numeric(10, 2), index=True)

    # Listing Details
    days_on_market = Column(Integer, default=0)
    listing_url = Column(Text)
    listing_status = Column(String(50), default="Active")  # Active, Pending, Sold
    listing_date = Column(DateTime)

    # Seller Score (composite metric)
    seller_score = Column(Numeric(5, 2))

    # Data Source Tracking
    data_source = Column(String(50))  # e.g., "rentcast", "manual", "redfin"
    fetched_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Source Citations
    price_source_name = Column(String(100))
    price_source_url = Column(Text)
    tax_source_name = Column(String(100))
    tax_source_url = Column(Text)

    def __repr__(self):
        return f"<Property(id={self.id}, address='{self.address}', price={self.price})>"
