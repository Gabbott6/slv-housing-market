"""
Configuration management for the SLV Housing Market application.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "SLV Housing Market"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/slv_housing"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # Data Sources
    DATA_SOURCE: str = "manual"  # Options: manual, rentcast, redfin, slc_county
    RENTCAST_API_KEY: Optional[str] = None

    # AI Service
    GOOGLE_API_KEY: Optional[str] = None

    # Mortgage Calculations
    DEFAULT_DOWN_PAYMENT_PERCENT: float = 20.0
    DEFAULT_MORTGAGE_RATE: float = 7.0  # Annual percentage
    DEFAULT_LOAN_TERM_YEARS: int = 30

    # Tax Rates
    SLC_PROPERTY_TAX_RATE: float = 0.0056  # 0.56% average for Salt Lake County

    # Insurance Estimates (annual)
    INSURANCE_RATE_LOW: float = 800.0  # For properties < $300k
    INSURANCE_RATE_MID: float = 1200.0  # For properties $300k-$500k
    INSURANCE_RATE_HIGH: float = 1800.0  # For properties > $500k

    # API Settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
