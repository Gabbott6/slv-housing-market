"""
Housing code model for storing building codes, ordinances, and regulations.
Used for AI-powered Q&A system (RAG).
"""
from sqlalchemy import Column, Integer, String, Text, Date, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from ..database import Base


class HousingCode(Base):
    """Housing code and regulation model."""

    __tablename__ = "housing_codes"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Code Identification
    code_section = Column(String(50), index=True)  # e.g., "Title 15.1.2"
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    # Jurisdiction and Category
    jurisdiction = Column(String(100), index=True)  # e.g., "Salt Lake County", "Utah State"
    category = Column(String(100))  # e.g., "Building Codes", "Zoning", "Fire Safety"

    # Source Information
    source_name = Column(String(100))  # e.g., "Municode Library", "UpCodes"
    source_url = Column(Text)
    last_updated = Column(Date)

    # Full-text search column (for PostgreSQL)
    # This will be populated with a trigger or computed column
    search_vector = Column(TSVECTOR)

    def __repr__(self):
        return f"<HousingCode(section='{self.code_section}', jurisdiction='{self.jurisdiction}')>"


# Create full-text search index
Index(
    'idx_housing_codes_search',
    HousingCode.search_vector,
    postgresql_using='gin'
)
