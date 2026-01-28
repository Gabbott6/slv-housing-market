"""
Base interface for property data sources.
Implements the adapter pattern for easy switching between data sources.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...models.property import Property


class PropertyDataSource(ABC):
    """Abstract base class for property data sources."""

    @abstractmethod
    async def fetch_properties(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Property]:
        """
        Fetch properties from the data source.

        Args:
            filters: Optional filters (price_min, price_max, beds, baths, etc.)
            limit: Maximum number of properties to fetch

        Returns:
            List of Property model instances
        """
        pass

    @abstractmethod
    async def get_property_details(self, property_id: str) -> Optional[Property]:
        """
        Get detailed information for a specific property.

        Args:
            property_id: Unique identifier for the property

        Returns:
            Property model instance or None if not found
        """
        pass

    @abstractmethod
    async def refresh_data(self) -> int:
        """
        Refresh/update property data from the source.

        Returns:
            Number of properties updated
        """
        pass

    def get_source_name(self) -> str:
        """
        Get the name of this data source.

        Returns:
            Source name (e.g., "RentCast API", "Manual Upload")
        """
        return self.__class__.__name__


class Source:
    """Data source citation model."""

    def __init__(self, name: str, url: str, date: str):
        self.name = name
        self.url = url
        self.date = date

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "url": self.url,
            "date": self.date
        }
