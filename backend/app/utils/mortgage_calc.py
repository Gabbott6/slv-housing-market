"""
Mortgage and housing cost calculation utilities.
"""
from typing import Dict
from decimal import Decimal


def calculate_monthly_mortgage(
    property_price: float,
    down_payment_percent: float = 20.0,
    annual_rate: float = 7.0,
    loan_term_years: int = 30
) -> float:
    """
    Calculate monthly mortgage payment using standard amortization formula.

    Args:
        property_price: Total property price in dollars
        down_payment_percent: Down payment as percentage (e.g., 20 for 20%)
        annual_rate: Annual interest rate as percentage (e.g., 7 for 7%)
        loan_term_years: Loan term in years (typically 30 or 15)

    Returns:
        Monthly mortgage payment in dollars
    """
    # Calculate loan amount after down payment
    down_payment = property_price * (down_payment_percent / 100)
    loan_amount = property_price - down_payment

    # Convert annual rate to monthly rate
    monthly_rate = (annual_rate / 100) / 12

    # Total number of payments
    num_payments = loan_term_years * 12

    # Handle edge case: if rate is 0, simple division
    if monthly_rate == 0:
        return loan_amount / num_payments

    # Standard mortgage formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
    monthly_payment = loan_amount * (
        monthly_rate * (1 + monthly_rate) ** num_payments
    ) / (
        (1 + monthly_rate) ** num_payments - 1
    )

    return round(monthly_payment, 2)


def calculate_monthly_property_tax(property_price: float, tax_rate: float = 0.0056) -> float:
    """
    Calculate monthly property tax.

    Args:
        property_price: Property price in dollars
        tax_rate: Annual property tax rate as decimal (e.g., 0.0056 for 0.56%)

    Returns:
        Monthly property tax in dollars
    """
    annual_tax = property_price * tax_rate
    monthly_tax = annual_tax / 12
    return round(monthly_tax, 2)


def estimate_monthly_insurance(property_price: float) -> float:
    """
    Estimate monthly homeowners insurance based on property price.
    Uses industry standard estimates.

    Args:
        property_price: Property price in dollars

    Returns:
        Estimated monthly insurance cost in dollars
    """
    # Annual insurance estimates by price tier
    if property_price < 300000:
        annual_insurance = 800.0
    elif property_price < 500000:
        annual_insurance = 1200.0
    else:
        annual_insurance = 1800.0

    monthly_insurance = annual_insurance / 12
    return round(monthly_insurance, 2)


def calculate_total_monthly_cost(
    property_price: float,
    hoa_fee: float = 0.0,
    tax_rate: float = 0.0056,
    down_payment_percent: float = 20.0,
    mortgage_rate: float = 7.0,
    loan_term_years: int = 30
) -> Dict[str, float]:
    """
    Calculate all monthly housing costs.

    Args:
        property_price: Property price in dollars
        hoa_fee: Monthly HOA fee (defaults to 0)
        tax_rate: Annual property tax rate as decimal
        down_payment_percent: Down payment percentage
        mortgage_rate: Annual mortgage interest rate percentage
        loan_term_years: Loan term in years

    Returns:
        Dictionary with breakdown of all monthly costs
    """
    monthly_mortgage = calculate_monthly_mortgage(
        property_price,
        down_payment_percent,
        mortgage_rate,
        loan_term_years
    )

    monthly_tax = calculate_monthly_property_tax(property_price, tax_rate)
    monthly_insurance = estimate_monthly_insurance(property_price)
    monthly_hoa = hoa_fee

    total_monthly = monthly_mortgage + monthly_tax + monthly_insurance + monthly_hoa

    return {
        "monthly_mortgage": round(monthly_mortgage, 2),
        "monthly_taxes": round(monthly_tax, 2),
        "monthly_insurance": round(monthly_insurance, 2),
        "monthly_hoa": round(monthly_hoa, 2),
        "total_monthly_cost": round(total_monthly, 2)
    }


def calculate_seller_score(days_on_market: int, price_change_percent: float = 0.0) -> float:
    """
    Calculate seller score proxy metric.
    Since true seller ratings aren't available, we use:
    - Days on market (lower is better)
    - Price stability (less change is better)

    Args:
        days_on_market: Number of days property has been listed
        price_change_percent: Percentage change in price (negative = price drop)

    Returns:
        Seller score (0-100, higher is better)
    """
    # Base score from days on market (inverse relationship)
    # Score decreases as days increase
    if days_on_market == 0:
        dom_score = 100
    else:
        # Use exponential decay: score = 100 * e^(-days/90)
        import math
        dom_score = 100 * math.exp(-days_on_market / 90)

    # Price stability factor (penalize large price drops)
    if price_change_percent >= 0:
        # Price increase or stable = good
        price_factor = 1.0
    else:
        # Price drop = penalty
        # -5% drop = 0.9 factor, -10% drop = 0.8 factor, etc.
        price_factor = max(0.5, 1.0 + (price_change_percent / 100))

    # Combined score
    seller_score = dom_score * price_factor

    return round(seller_score, 2)
