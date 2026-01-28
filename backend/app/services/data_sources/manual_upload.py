"""
Manual CSV upload data source.
Allows users to upload their own property data via CSV files.
"""
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime
from .base import PropertyDataSource, Source
from ...models.property import Property
from ..calculator import calculate_property_costs


class ManualUploadDataSource(PropertyDataSource):
    """Data source for manually uploaded CSV files."""

    def __init__(self, db_session):
        self.db = db_session
        self.source_name = "Manual Upload"

    async def fetch_properties(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Property]:
        """
        Fetch properties from the database (previously uploaded).

        Args:
            filters: Optional filters
            limit: Maximum number of properties

        Returns:
            List of Property instances
        """
        query = self.db.query(Property).filter(
            Property.data_source == "manual"
        )

        # Apply filters
        if filters:
            if "price_min" in filters:
                query = query.filter(Property.price >= filters["price_min"])
            if "price_max" in filters:
                query = query.filter(Property.price <= filters["price_max"])
            if "beds" in filters:
                query = query.filter(Property.beds >= filters["beds"])
            if "baths" in filters:
                query = query.filter(Property.baths >= filters["baths"])
            if "city" in filters:
                query = query.filter(Property.city == filters["city"])

        return query.limit(limit).all()

    async def get_property_details(self, property_id: str) -> Optional[Property]:
        """Get specific property by ID."""
        return self.db.query(Property).filter(
            Property.id == int(property_id),
            Property.data_source == "manual"
        ).first()

    async def refresh_data(self) -> int:
        """Manual uploads don't auto-refresh."""
        return 0

    async def upload_csv(self, csv_file_path: str) -> int:
        """
        Upload properties from a CSV file.

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

        Args:
            csv_file_path: Path to CSV file

        Returns:
            Number of properties uploaded
        """
        # Read CSV
        df = pd.read_csv(csv_file_path)

        # Validate required columns
        required_columns = ["address", "price"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        properties_added = 0

        for _, row in df.iterrows():
            # Create property instance
            property_obj = Property(
                address=row["address"],
                city=row.get("city", "Salt Lake City"),
                state="UT",
                price=float(row["price"]),
                beds=int(row.get("beds", 0)) if pd.notna(row.get("beds")) else None,
                baths=float(row.get("baths", 0)) if pd.notna(row.get("baths")) else None,
                sqft=int(row.get("sqft", 0)) if pd.notna(row.get("sqft")) else None,
                property_type=row.get("property_type", "Single Family"),
                hoa_fee=float(row.get("hoa_fee", 0)) if pd.notna(row.get("hoa_fee")) else 0.0,
                listing_url=row.get("listing_url", ""),
                data_source="manual",
                fetched_at=datetime.now(),
                price_source_name=self.source_name,
                tax_source_name="Salt Lake County Assessor (Default)",
                listing_status="Active"
            )

            # Calculate price per sqft if sqft available
            if property_obj.sqft and property_obj.sqft > 0:
                property_obj.price_per_sqft = float(property_obj.price) / property_obj.sqft

            # Calculate monthly costs
            property_obj = calculate_property_costs(property_obj)

            # Add to database
            self.db.add(property_obj)
            properties_added += 1

        # Commit all properties
        self.db.commit()

        return properties_added

    async def upload_from_dataframe(self, df: pd.DataFrame) -> int:
        """
        Upload properties from a pandas DataFrame.

        Args:
            df: DataFrame with property data

        Returns:
            Number of properties uploaded
        """
        # Validate required columns
        required_columns = ["address", "price"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        properties_added = 0

        for _, row in df.iterrows():
            property_obj = Property(
                address=row["address"],
                city=row.get("city", "Salt Lake City"),
                state="UT",
                price=float(row["price"]),
                beds=int(row.get("beds", 0)) if pd.notna(row.get("beds")) else None,
                baths=float(row.get("baths", 0)) if pd.notna(row.get("baths")) else None,
                sqft=int(row.get("sqft", 0)) if pd.notna(row.get("sqft")) else None,
                property_type=row.get("property_type", "Single Family"),
                hoa_fee=float(row.get("hoa_fee", 0)) if pd.notna(row.get("hoa_fee")) else 0.0,
                listing_url=row.get("listing_url", ""),
                data_source="manual",
                fetched_at=datetime.now(),
                price_source_name=self.source_name,
                tax_source_name="Salt Lake County Assessor (Default)"
            )

            # Calculate price per sqft
            if property_obj.sqft and property_obj.sqft > 0:
                property_obj.price_per_sqft = float(property_obj.price) / property_obj.sqft

            # Calculate costs
            property_obj = calculate_property_costs(property_obj)

            self.db.add(property_obj)
            properties_added += 1

        self.db.commit()
        return properties_added
