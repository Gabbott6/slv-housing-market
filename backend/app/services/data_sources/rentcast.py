"""
RentCast API data source adapter.
Provides access to 140M+ property records via RentCast API.
"""
from typing import List, Optional, Dict, Any
import httpx
from datetime import datetime
from .base import PropertyDataSource, Source
from ...models.property import Property
from ...config import settings
from ..calculator import calculate_property_costs


class RentCastDataSource(PropertyDataSource):
    """RentCast API data source."""

    BASE_URL = "https://api.rentcast.io/v1"

    def __init__(self, db_session, api_key: Optional[str] = None):
        self.db = db_session
        self.api_key = api_key or settings.RENTCAST_API_KEY
        self.source_name = "RentCast API"
        self.source_url = "https://www.rentcast.io"

        if not self.api_key:
            raise ValueError("RentCast API key is required")

    async def fetch_properties(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[Property]:
        """
        Fetch properties from RentCast API.

        Args:
            filters: Search filters (city, state, price_min, price_max, etc.)
            limit: Maximum properties to fetch (RentCast free tier: 50/month)

        Returns:
            List of Property instances
        """
        # Build query parameters
        params = {
            "state": filters.get("state", "UT") if filters else "UT",
            "limit": min(limit, 50)  # RentCast free tier limit
        }

        if filters:
            if "city" in filters:
                params["city"] = filters["city"]
            if "price_min" in filters:
                params["priceMin"] = filters["price_min"]
            if "price_max" in filters:
                params["priceMax"] = filters["price_max"]
            if "beds" in filters:
                params["bedsMin"] = filters["beds"]
            if "baths" in filters:
                params["bathsMin"] = filters["baths"]

        headers = {
            "X-API-Key": self.api_key,
            "accept": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/listings/sale",
                params=params,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        properties = []
        for listing in data.get("listings", []):
            property_obj = self._parse_listing(listing)
            properties.append(property_obj)

        return properties

    async def get_property_details(self, property_id: str) -> Optional[Property]:
        """
        Get detailed property information by ID.

        Args:
            property_id: RentCast property ID or address

        Returns:
            Property instance or None
        """
        headers = {
            "X-API-Key": self.api_key,
            "accept": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/properties/{property_id}",
                headers=headers,
                timeout=30.0
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

        return self._parse_listing(data)

    async def refresh_data(self) -> int:
        """
        Refresh property data from RentCast.
        Note: Limited by free tier (50 calls/month).

        Returns:
            Number of properties updated
        """
        # Fetch latest Salt Lake County listings
        properties = await self.fetch_properties(
            filters={"city": "Salt Lake City", "state": "UT"},
            limit=50
        )

        count = 0
        for prop in properties:
            # Check if property already exists
            existing = self.db.query(Property).filter(
                Property.address == prop.address,
                Property.data_source == "rentcast"
            ).first()

            if existing:
                # Update existing
                for key, value in prop.__dict__.items():
                    if not key.startswith("_"):
                        setattr(existing, key, value)
                count += 1
            else:
                # Add new
                self.db.add(prop)
                count += 1

        self.db.commit()
        return count

    def _parse_listing(self, listing_data: Dict[str, Any]) -> Property:
        """Parse RentCast listing JSON into Property model."""
        property_obj = Property(
            address=listing_data.get("addressLine1", ""),
            city=listing_data.get("city", ""),
            state=listing_data.get("state", "UT"),
            zip_code=listing_data.get("zipCode", ""),
            price=float(listing_data.get("price", 0)),
            beds=int(listing_data.get("bedrooms", 0)),
            baths=float(listing_data.get("bathrooms", 0)),
            sqft=int(listing_data.get("squareFootage", 0)),
            property_type=listing_data.get("propertyType", "Single Family"),
            year_built=int(listing_data.get("yearBuilt", 0)) if listing_data.get("yearBuilt") else None,
            lot_size=float(listing_data.get("lotSize", 0)) if listing_data.get("lotSize") else None,
            listing_url=listing_data.get("url", ""),
            days_on_market=int(listing_data.get("daysOnMarket", 0)),
            data_source="rentcast",
            fetched_at=datetime.now(),
            price_source_name=self.source_name,
            price_source_url=self.source_url,
            tax_source_name="RentCast API",
            listing_status="Active"
        )

        # Calculate price per sqft
        if property_obj.sqft and property_obj.sqft > 0:
            property_obj.price_per_sqft = float(property_obj.price) / property_obj.sqft

        # Calculate all monthly costs
        property_obj = calculate_property_costs(property_obj)

        return property_obj
