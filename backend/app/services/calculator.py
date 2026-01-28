"""
Property cost calculation service.
Applies calculations to property models.
"""
from typing import Dict, Optional
from ..models.property import Property
from ..utils.mortgage_calc import (
    calculate_total_monthly_cost,
    calculate_seller_score
)
from ..config import settings


def calculate_property_costs(
    property_obj: Property,
    down_payment_percent: Optional[float] = None,
    mortgage_rate: Optional[float] = None,
    loan_term_years: Optional[int] = None
) -> Property:
    """
    Calculate all monthly costs for a property and update the model.

    Args:
        property_obj: Property model instance
        down_payment_percent: Custom down payment % (uses default if None)
        mortgage_rate: Custom mortgage rate % (uses default if None)
        loan_term_years: Custom loan term (uses default if None)

    Returns:
        Updated property object with calculated costs
    """
    # Use defaults from settings if not provided
    down_payment = down_payment_percent or settings.DEFAULT_DOWN_PAYMENT_PERCENT
    rate = mortgage_rate or settings.DEFAULT_MORTGAGE_RATE
    term = loan_term_years or settings.DEFAULT_LOAN_TERM_YEARS

    # Get tax rate from property or use default
    tax_rate = float(property_obj.tax_rate) if property_obj.tax_rate else settings.SLC_PROPERTY_TAX_RATE

    # Calculate all costs
    costs = calculate_total_monthly_cost(
        property_price=float(property_obj.price),
        hoa_fee=float(property_obj.hoa_fee) if property_obj.hoa_fee else 0.0,
        tax_rate=tax_rate,
        down_payment_percent=down_payment,
        mortgage_rate=rate,
        loan_term_years=term
    )

    # Update property model
    property_obj.monthly_mortgage = costs["monthly_mortgage"]
    property_obj.monthly_taxes = costs["monthly_taxes"]
    property_obj.monthly_insurance = costs["monthly_insurance"]
    property_obj.monthly_hoa = costs["monthly_hoa"]
    property_obj.total_monthly_cost = costs["total_monthly_cost"]

    # Calculate seller score if we have days on market
    if property_obj.days_on_market is not None:
        property_obj.seller_score = calculate_seller_score(
            days_on_market=property_obj.days_on_market
        )

    return property_obj


def get_cost_breakdown(property_obj: Property) -> Dict[str, float]:
    """
    Get a dictionary with all cost breakdowns for display.

    Args:
        property_obj: Property model instance

    Returns:
        Dictionary with all cost information
    """
    return {
        "price": float(property_obj.price),
        "monthly_mortgage": float(property_obj.monthly_mortgage or 0),
        "monthly_taxes": float(property_obj.monthly_taxes or 0),
        "monthly_insurance": float(property_obj.monthly_insurance or 0),
        "monthly_hoa": float(property_obj.monthly_hoa or 0),
        "total_monthly_cost": float(property_obj.total_monthly_cost or 0),
        "seller_score": float(property_obj.seller_score or 0)
    }
