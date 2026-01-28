"""
AI-powered property analysis service using Google Gemini.
Provides property summaries, recommendations, comparisons, and market analysis.
"""
from typing import List, Dict, Any, Optional
import json
import re
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.property import Property
from ..config import settings
from .rate_limiter import GeminiRateLimiter
from .ai_cache import AIResponseCache


class PropertyAnalysisService:
    """AI-powered property analysis using Google Gemini."""

    def __init__(self, db_session: Session, api_key: Optional[str] = None):
        """
        Initialize property analysis service.

        Args:
            db_session: Database session
            api_key: Google API key (uses settings if not provided)
        """
        self.db = db_session
        self.api_key = api_key or settings.GOOGLE_API_KEY

        if not self.api_key:
            raise ValueError("Google API key is required for AI analysis")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.rate_limiter = GeminiRateLimiter()
        self.cache = AIResponseCache()

    async def summarize_properties(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max_properties: int = 50
    ) -> Dict[str, Any]:
        """
        Generate AI summary of properties matching filters.

        Args:
            filters: Property filters (price_min, price_max, beds, baths, city)
            max_properties: Maximum properties to analyze

        Returns:
            Dictionary with summary, insights, and statistics
        """
        # Generate cache key
        cache_params = {
            "filters": filters or {},
            "max_properties": max_properties
        }
        cache_key = self.cache.generate_key("summary", **cache_params)

        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

        # Fetch properties from database
        properties = self._fetch_properties(filters, limit=max_properties)

        if not properties:
            return {
                "summary": "No properties found matching your criteria.",
                "key_insights": [],
                "statistics": {},
                "properties_analyzed": 0,
                "confidence": "low",
                "from_cache": False
            }

        # Calculate statistics
        statistics = self._calculate_statistics(properties)

        # Format properties as context for Gemini
        context = self._format_properties_as_context(properties)

        # Build prompt
        prompt = self._build_summary_prompt(context, len(properties), statistics)

        # Call Gemini with rate limiting
        try:
            await self.rate_limiter.acquire()
            response = self.model.generate_content(prompt)
            ai_text = response.text

            # Parse response
            result = self._parse_summary_response(ai_text, statistics, len(properties))

        except Exception as e:
            # Fallback to basic summary without AI
            result = self._generate_fallback_summary(properties, statistics)
            result["error"] = str(e)

        # Cache for 1 hour
        await self.cache.set(cache_key, result, ttl=3600)

        result["from_cache"] = False
        return result

    def _fetch_properties(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[Property]:
        """Fetch properties from database with filters."""
        query = self.db.query(Property)

        if filters:
            # Apply filters
            if "price_min" in filters and filters["price_min"]:
                query = query.filter(Property.price >= filters["price_min"])
            if "price_max" in filters and filters["price_max"]:
                query = query.filter(Property.price <= filters["price_max"])
            if "beds" in filters and filters["beds"]:
                query = query.filter(Property.beds >= filters["beds"])
            if "baths" in filters and filters["baths"]:
                query = query.filter(Property.baths >= filters["baths"])
            if "city" in filters and filters["city"]:
                query = query.filter(Property.city.ilike(f"%{filters['city']}%"))

        # Order by total monthly cost (ascending)
        query = query.order_by(Property.total_monthly_cost.asc())

        return query.limit(limit).all()

    def _calculate_statistics(self, properties: List[Property]) -> Dict[str, Any]:
        """Calculate statistics from properties."""
        if not properties:
            return {}

        prices = [float(p.price) for p in properties if p.price]
        monthly_costs = [
            float(p.total_monthly_cost)
            for p in properties
            if p.total_monthly_cost
        ]
        price_per_sqft = [
            float(p.price_per_sqft)
            for p in properties
            if p.price_per_sqft
        ]

        # City distribution
        city_counts = {}
        for p in properties:
            if p.city:
                city_counts[p.city] = city_counts.get(p.city, 0) + 1

        # Most common city
        most_common_city = max(city_counts.items(), key=lambda x: x[1])[0] if city_counts else None

        return {
            "count": len(properties),
            "avg_price": sum(prices) / len(prices) if prices else 0,
            "median_price": sorted(prices)[len(prices) // 2] if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "avg_monthly_cost": sum(monthly_costs) / len(monthly_costs) if monthly_costs else 0,
            "avg_price_per_sqft": sum(price_per_sqft) / len(price_per_sqft) if price_per_sqft else 0,
            "most_common_city": most_common_city,
            "cities": list(city_counts.keys())
        }

    def _format_properties_as_context(self, properties: List[Property]) -> str:
        """Format properties as context for Gemini."""
        context_parts = []

        for i, prop in enumerate(properties[:50], 1):  # Limit to 50 for token management
            context_parts.append(
                f"Property {i}:\n"
                f"  Address: {prop.address}, {prop.city or 'N/A'}\n"
                f"  Price: ${prop.price:,.0f}\n"
                f"  Beds/Baths: {prop.beds or 'N/A'} bed, {prop.baths or 'N/A'} bath\n"
                f"  Size: {prop.sqft or 'N/A'} sqft\n"
                f"  Monthly Cost: ${prop.total_monthly_cost or 'N/A'}\n"
                f"  Price/sqft: ${prop.price_per_sqft or 'N/A'}\n"
                f"  HOA: ${prop.hoa_fee or 0}/mo\n"
                f"  Days on Market: {prop.days_on_market or 'N/A'}\n"
            )

        return "\n".join(context_parts)

    def _build_summary_prompt(
        self,
        context: str,
        property_count: int,
        statistics: Dict[str, Any]
    ) -> str:
        """Build summary prompt for Gemini."""
        system_context = """You are an expert real estate analyst for Salt Lake Valley with deep knowledge of:
- Local market conditions and pricing trends
- Neighborhood characteristics (Sandy, Draper, Provo, South Jordan, etc.)
- Property valuation and investment potential
- Mortgage calculations and cost analysis

Your goal is to provide accurate, data-driven insights that help buyers make informed decisions."""

        prompt = f"""{system_context}

Analyze these {property_count} properties from Salt Lake Valley and provide a comprehensive market summary.

PROPERTIES DATA:
{context}

STATISTICS:
- Average Price: ${statistics.get('avg_price', 0):,.0f}
- Median Price: ${statistics.get('median_price', 0):,.0f}
- Price Range: ${statistics.get('min_price', 0):,.0f} - ${statistics.get('max_price', 0):,.0f}
- Average Monthly Cost: ${statistics.get('avg_monthly_cost', 0):,.0f}
- Average Price/sqft: ${statistics.get('avg_price_per_sqft', 0):.2f}
- Most Common City: {statistics.get('most_common_city', 'N/A')}

Please provide:
1. Overall market summary (2-3 sentences)
2. Key insights (3-5 bullet points) about best values, trends, or notable properties
3. Recommendations by buyer type (first-time buyer, family, investor)

Format your response as JSON with this structure:
{{
  "summary": "Overall market summary...",
  "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
  "buyer_recommendations": {{
    "first_time_buyer": "Recommendation for first-time buyers...",
    "family": "Recommendation for families...",
    "investor": "Recommendation for investors..."
  }}
}}

Be specific, reference actual data, and provide actionable insights."""

        return prompt

    def _parse_summary_response(
        self,
        ai_text: str,
        statistics: Dict[str, Any],
        property_count: int
    ) -> Dict[str, Any]:
        """Parse AI response and structure it."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                # Fallback: treat entire response as summary
                parsed = {"summary": ai_text, "key_insights": []}

            return {
                "summary": parsed.get("summary", ai_text),
                "key_insights": parsed.get("key_insights", []),
                "buyer_recommendations": parsed.get("buyer_recommendations", {}),
                "statistics": statistics,
                "properties_analyzed": property_count,
                "confidence": "high" if property_count >= 10 else "medium"
            }

        except json.JSONDecodeError:
            # Fallback to basic structure
            return {
                "summary": ai_text,
                "key_insights": [],
                "buyer_recommendations": {},
                "statistics": statistics,
                "properties_analyzed": property_count,
                "confidence": "medium"
            }

    def _generate_fallback_summary(
        self,
        properties: List[Property],
        statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic summary without AI when API fails."""
        summary = (
            f"Found {len(properties)} properties in Salt Lake Valley. "
            f"Average price is ${statistics.get('avg_price', 0):,.0f} with "
            f"monthly costs averaging ${statistics.get('avg_monthly_cost', 0):,.0f}."
        )

        insights = [
            f"Price range: ${statistics.get('min_price', 0):,.0f} - ${statistics.get('max_price', 0):,.0f}",
            f"Most properties in: {statistics.get('most_common_city', 'Various cities')}",
            f"Average price per sqft: ${statistics.get('avg_price_per_sqft', 0):.2f}"
        ]

        return {
            "summary": summary,
            "key_insights": insights,
            "buyer_recommendations": {},
            "statistics": statistics,
            "properties_analyzed": len(properties),
            "confidence": "low"
        }

    async def recommend_properties(
        self,
        criteria: Dict[str, Any],
        max_recommendations: int = 5
    ) -> Dict[str, Any]:
        """
        Generate AI-powered property recommendations based on buyer criteria.

        Args:
            criteria: Buyer criteria (budget_max, beds_min, baths_min, priorities, lifestyle, city_preference)
            max_recommendations: Maximum number of recommendations to return

        Returns:
            Dictionary with recommended properties and explanations
        """
        # Generate cache key
        cache_key = self.cache.generate_key("recommend", **criteria)

        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

        # Build filters from criteria
        filters = {}
        if "budget_max" in criteria and criteria["budget_max"]:
            filters["price_max"] = criteria["budget_max"]
        if "beds_min" in criteria and criteria["beds_min"]:
            filters["beds"] = criteria["beds_min"]
        if "baths_min" in criteria and criteria["baths_min"]:
            filters["baths"] = criteria["baths_min"]
        if "city_preference" in criteria and criteria["city_preference"]:
            filters["city"] = criteria["city_preference"]

        # Fetch matching properties
        properties = self._fetch_properties(filters, limit=20)

        if not properties:
            return {
                "recommendations": [],
                "message": "No properties found matching your criteria.",
                "confidence": "low",
                "from_cache": False
            }

        # Score properties based on criteria
        scored_properties = self._score_properties(properties, criteria)

        # Get top recommendations
        top_properties = scored_properties[:max_recommendations]

        # Format properties for AI context
        context = self._format_recommendations_context(top_properties, criteria)

        # Build AI prompt
        prompt = self._build_recommendation_prompt(context, criteria, len(properties))

        # Call Gemini with rate limiting
        try:
            await self.rate_limiter.acquire()
            response = self.model.generate_content(prompt)
            ai_text = response.text

            # Parse response
            result = self._parse_recommendation_response(ai_text, top_properties)

        except Exception as e:
            # Fallback without AI
            result = self._generate_fallback_recommendations(top_properties)
            result["error"] = str(e)

        # Cache for 30 minutes
        await self.cache.set(cache_key, result, ttl=1800)

        result["from_cache"] = False
        return result

    def _score_properties(
        self,
        properties: List[Property],
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Score properties based on buyer criteria."""
        scored = []

        # Get priority weights (default to equal if not specified)
        priorities = criteria.get("priorities", {})
        monthly_cost_weight = float(priorities.get("monthly_cost", 25))
        location_weight = float(priorities.get("location", 25))
        value_weight = float(priorities.get("value", 25))
        space_weight = float(priorities.get("space", 25))

        # Normalize weights to sum to 100
        total_weight = monthly_cost_weight + location_weight + value_weight + space_weight
        if total_weight == 0:
            total_weight = 100.0

        for prop in properties:
            scores = {}

            # Monthly cost score (lower is better)
            if prop.total_monthly_cost:
                max_monthly = max(float(p.total_monthly_cost) for p in properties if p.total_monthly_cost)
                min_monthly = min(float(p.total_monthly_cost) for p in properties if p.total_monthly_cost)
                if max_monthly > min_monthly:
                    scores["monthly_cost"] = 100 * (1 - (float(prop.total_monthly_cost) - min_monthly) / (max_monthly - min_monthly))
                else:
                    scores["monthly_cost"] = 100
            else:
                scores["monthly_cost"] = 50

            # Value score (price per sqft - lower is better)
            if prop.price_per_sqft:
                price_sqfts = [float(p.price_per_sqft) for p in properties if p.price_per_sqft]
                if price_sqfts:
                    max_psf = max(price_sqfts)
                    min_psf = min(price_sqfts)
                    if max_psf > min_psf:
                        scores["value"] = 100 * (1 - (float(prop.price_per_sqft) - min_psf) / (max_psf - min_psf))
                    else:
                        scores["value"] = 100
            else:
                scores["value"] = 50

            # Space score (sqft - higher is better)
            if prop.sqft:
                sqfts = [float(p.sqft) for p in properties if p.sqft]
                if sqfts:
                    max_sqft = max(sqfts)
                    min_sqft = min(sqfts)
                    if max_sqft > min_sqft:
                        scores["space"] = 100 * (float(prop.sqft) - min_sqft) / (max_sqft - min_sqft)
                    else:
                        scores["space"] = 100
            else:
                scores["space"] = 50

            # Location score (city preference match)
            city_pref = criteria.get("city_preference", "").lower()
            if city_pref and prop.city and city_pref in prop.city.lower():
                scores["location"] = 100
            elif prop.city:
                scores["location"] = 60  # Neutral if city specified but not matching
            else:
                scores["location"] = 50

            # Calculate weighted total score
            total_score = (
                scores["monthly_cost"] * (monthly_cost_weight / total_weight) +
                scores["value"] * (value_weight / total_weight) +
                scores["space"] * (space_weight / total_weight) +
                scores["location"] * (location_weight / total_weight)
            )

            scored.append({
                "property": prop,
                "score": round(total_score, 1),
                "scores": scores
            })

        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def _format_recommendations_context(
        self,
        scored_properties: List[Dict[str, Any]],
        criteria: Dict[str, Any]
    ) -> str:
        """Format scored properties as context for Gemini."""
        context_parts = []

        for i, item in enumerate(scored_properties, 1):
            prop = item["property"]
            score = item["score"]

            context_parts.append(
                f"Property {i} (Match Score: {score}/100):\n"
                f"  Address: {prop.address}, {prop.city or 'N/A'}\n"
                f"  Price: ${prop.price:,.0f}\n"
                f"  Beds/Baths: {prop.beds or 'N/A'} bed, {prop.baths or 'N/A'} bath\n"
                f"  Size: {prop.sqft or 'N/A'} sqft\n"
                f"  Monthly Cost: ${prop.total_monthly_cost or 'N/A'}\n"
                f"  Price/sqft: ${prop.price_per_sqft or 'N/A'}\n"
                f"  HOA: ${prop.hoa_fee or 0}/mo\n"
                f"  Days on Market: {prop.days_on_market or 'N/A'}\n"
                f"  Property Type: {prop.property_type or 'N/A'}\n"
            )

        return "\n".join(context_parts)

    def _build_recommendation_prompt(
        self,
        context: str,
        criteria: Dict[str, Any],
        total_properties: int
    ) -> str:
        """Build recommendation prompt for Gemini."""
        lifestyle = criteria.get("lifestyle", "buyer")
        budget = criteria.get("budget_max", "not specified")

        system_context = """You are an expert real estate advisor for Salt Lake Valley with deep knowledge of:
- Local market conditions and pricing trends
- Neighborhood characteristics (Sandy, Draper, Provo, South Jordan, etc.)
- Property valuation and investment potential
- Buyer needs analysis and matching

Your goal is to provide accurate, personalized property recommendations that help buyers make informed decisions."""

        prompt = f"""{system_context}

A {lifestyle} is looking for properties with these criteria:
- Budget: ${budget:,} max
- Bedrooms: {criteria.get('beds_min', 'any')}+ bedrooms
- Bathrooms: {criteria.get('baths_min', 'any')}+ bathrooms
- City Preference: {criteria.get('city_preference', 'any')}
- Priorities: {criteria.get('priorities', 'balanced')}

I've scored {total_properties} properties and here are the top matches:

{context}

For each of the top 3 properties, provide:
1. A match explanation (2-3 sentences on why this property fits their needs)
2. Top 3 pros (specific advantages for this buyer)
3. Top 2-3 cons (honest concerns or tradeoffs)

Format your response as JSON:
{{
  "recommendations": [
    {{
      "property_number": 1,
      "match_explanation": "...",
      "pros": ["Pro 1", "Pro 2", "Pro 3"],
      "cons": ["Con 1", "Con 2"]
    }}
  ]
}}

Be specific, honest, and focused on what matters to this {lifestyle}."""

        return prompt

    def _parse_recommendation_response(
        self,
        ai_text: str,
        scored_properties: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse AI recommendation response."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                parsed = {"recommendations": []}

            # Build result with property details
            recommendations = []
            for i, rec in enumerate(parsed.get("recommendations", [])):
                if i < len(scored_properties):
                    prop_data = scored_properties[i]
                    recommendations.append({
                        "property_id": prop_data["property"].id,
                        "address": prop_data["property"].address,
                        "city": prop_data["property"].city,
                        "price": float(prop_data["property"].price),
                        "match_score": prop_data["score"],
                        "match_explanation": rec.get("match_explanation", ""),
                        "pros": rec.get("pros", []),
                        "cons": rec.get("cons", [])
                    })

            return {
                "recommendations": recommendations,
                "message": f"Found {len(recommendations)} great matches for you!",
                "confidence": "high" if len(recommendations) >= 3 else "medium"
            }

        except json.JSONDecodeError:
            return self._generate_fallback_recommendations(scored_properties)

    def _generate_fallback_recommendations(
        self,
        scored_properties: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate basic recommendations without AI."""
        recommendations = []

        for i, item in enumerate(scored_properties[:3]):
            prop = item["property"]
            score = item["score"]

            recommendations.append({
                "property_id": prop.id,
                "address": prop.address,
                "city": prop.city,
                "price": float(prop.price),
                "match_score": score,
                "match_explanation": f"This property scored {score}/100 based on your criteria.",
                "pros": [
                    f"Monthly cost: ${float(prop.total_monthly_cost):,.0f}" if prop.total_monthly_cost else "Affordable",
                    f"{prop.beds} bedrooms, {prop.baths} bathrooms" if prop.beds else "Good layout",
                    f"{float(prop.sqft)} sqft of living space" if prop.sqft else "Spacious"
                ],
                "cons": [
                    "Limited details available for deeper analysis"
                ]
            })

        return {
            "recommendations": recommendations,
            "message": f"Found {len(recommendations)} properties matching your criteria.",
            "confidence": "medium"
        }

    async def compare_properties(
        self,
        property_ids: List[int],
        aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered comparison of multiple properties.

        Args:
            property_ids: List of 2-5 property IDs to compare
            aspects: Optional list of aspects to focus on

        Returns:
            Dictionary with comparison analysis and winners by category
        """
        if len(property_ids) < 2:
            raise ValueError("At least 2 properties required for comparison")
        if len(property_ids) > 5:
            raise ValueError("Maximum 5 properties can be compared at once")

        # Generate cache key
        cache_key = self.cache.generate_key(
            "compare",
            property_ids=sorted(property_ids),
            aspects=aspects or []
        )

        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

        # Fetch properties
        properties = self.db.query(Property).filter(
            Property.id.in_(property_ids)
        ).all()

        if len(properties) != len(property_ids):
            raise ValueError("One or more properties not found")

        # Sort properties by ID to maintain consistent ordering
        properties_dict = {p.id: p for p in properties}
        properties = [properties_dict[pid] for pid in property_ids]

        # Build comparison context
        context = self._format_comparison_context(properties)

        # Build prompt
        prompt = self._build_comparison_prompt(context, len(properties), aspects)

        # Call Gemini with rate limiting
        try:
            await self.rate_limiter.acquire()
            response = self.model.generate_content(prompt)
            ai_text = response.text

            # Parse response
            result = self._parse_comparison_response(ai_text, properties)

        except Exception as e:
            # Fallback without AI
            result = self._generate_fallback_comparison(properties)
            result["error"] = str(e)

        # Cache for 2 hours
        await self.cache.set(cache_key, result, ttl=7200)

        result["from_cache"] = False
        return result

    def _format_comparison_context(self, properties: List[Property]) -> str:
        """Format properties for comparison context."""
        context_parts = []

        for i, prop in enumerate(properties, 1):
            context_parts.append(
                f"Property {chr(64+i)} (ID: {prop.id}):\n"
                f"  Address: {prop.address}, {prop.city or 'N/A'}\n"
                f"  Price: ${prop.price:,.0f}\n"
                f"  Monthly Cost: ${prop.total_monthly_cost or 'N/A'}\n"
                f"  Beds/Baths: {prop.beds or 'N/A'} bed / {prop.baths or 'N/A'} bath\n"
                f"  Size: {prop.sqft or 'N/A'} sqft\n"
                f"  Price per sqft: ${prop.price_per_sqft or 'N/A'}\n"
                f"  HOA: ${prop.hoa_fee or 0}/month\n"
                f"  Property Tax: ${prop.property_tax or 'N/A'}/year\n"
                f"  Days on Market: {prop.days_on_market or 'N/A'}\n"
                f"  Year Built: {prop.year_built or 'N/A'}\n"
                f"  Property Type: {prop.property_type or 'N/A'}\n"
                f"  Seller Score: {prop.seller_score or 'N/A'}/100\n"
            )

        return "\n".join(context_parts)

    def _build_comparison_prompt(
        self,
        context: str,
        num_properties: int,
        aspects: Optional[List[str]] = None
    ) -> str:
        """Build comparison prompt for Gemini."""
        system_context = """You are an expert real estate analyst for Salt Lake Valley with deep knowledge of:
- Property valuation and comparison
- Local market conditions
- Investment analysis
- Buyer decision-making

Your goal is to provide objective, data-driven property comparisons that help buyers choose the best option for their needs."""

        aspects_str = ", ".join(aspects) if aspects else "all key factors"

        prompt = f"""{system_context}

Compare these {num_properties} properties objectively, focusing on {aspects_str}:

{context}

Provide:
1. Overall comparison summary (2-3 sentences)
2. Best for monthly budget (identify winner and explain why)
3. Best for space/value (identify winner and explain why)
4. Best for long-term investment (identify winner and explain why)
5. Best for location/lifestyle (identify winner and explain why)
6. Overall recommendation (which property and why)

Format your response as JSON:
{{
  "summary": "Overall comparison summary...",
  "winners": {{
    "monthly_budget": {{"property_letter": "A", "reason": "..."}},
    "space_value": {{"property_letter": "B", "reason": "..."}},
    "investment": {{"property_letter": "A", "reason": "..."}},
    "location": {{"property_letter": "C", "reason": "..."}}
  }},
  "overall_recommendation": {{"property_letter": "A", "reason": "..."}}
}}

Be specific and objective. Use actual numbers from the data."""

        return prompt

    def _parse_comparison_response(
        self,
        ai_text: str,
        properties: List[Property]
    ) -> Dict[str, Any]:
        """Parse AI comparison response."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                parsed = {}

            # Build property details for reference
            property_details = []
            for i, prop in enumerate(properties):
                property_details.append({
                    "property_id": prop.id,
                    "property_letter": chr(65 + i),  # A, B, C, etc.
                    "address": prop.address,
                    "city": prop.city,
                    "price": float(prop.price),
                    "monthly_cost": float(prop.total_monthly_cost) if prop.total_monthly_cost else None,
                    "sqft": prop.sqft,
                    "price_per_sqft": float(prop.price_per_sqft) if prop.price_per_sqft else None,
                })

            return {
                "summary": parsed.get("summary", "Comparison of selected properties"),
                "winners": parsed.get("winners", {}),
                "overall_recommendation": parsed.get("overall_recommendation", {}),
                "properties": property_details,
                "confidence": "high" if "winners" in parsed else "medium"
            }

        except json.JSONDecodeError:
            return self._generate_fallback_comparison(properties)

    def _generate_fallback_comparison(self, properties: List[Property]) -> Dict[str, Any]:
        """Generate basic comparison without AI."""
        # Calculate simple winners
        property_details = []
        for i, prop in enumerate(properties):
            property_details.append({
                "property_id": prop.id,
                "property_letter": chr(65 + i),
                "address": prop.address,
                "city": prop.city,
                "price": float(prop.price),
                "monthly_cost": float(prop.total_monthly_cost) if prop.total_monthly_cost else None,
                "sqft": prop.sqft,
                "price_per_sqft": float(prop.price_per_sqft) if prop.price_per_sqft else None,
            })

        # Find winners by simple comparison
        monthly_winner = min(
            enumerate(properties),
            key=lambda x: x[1].total_monthly_cost if x[1].total_monthly_cost else float('inf')
        )
        value_winner = min(
            enumerate(properties),
            key=lambda x: x[1].price_per_sqft if x[1].price_per_sqft else float('inf')
        )

        winners = {
            "monthly_budget": {
                "property_letter": chr(65 + monthly_winner[0]),
                "reason": f"Lowest monthly cost at ${monthly_winner[1].total_monthly_cost:,.0f}"
            },
            "space_value": {
                "property_letter": chr(65 + value_winner[0]),
                "reason": f"Best value at ${value_winner[1].price_per_sqft:.2f}/sqft"
            }
        }

        return {
            "summary": f"Comparing {len(properties)} properties based on available data.",
            "winners": winners,
            "overall_recommendation": winners["monthly_budget"],
            "properties": property_details,
            "confidence": "low"
        }

    def sanitize_input(self, text: str, max_length: int = 500) -> str:
        """
        Sanitize user input to prevent prompt injection.

        Args:
            text: User input text
            max_length: Maximum allowed length

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Patterns that might indicate prompt injection
        dangerous_patterns = [
            r"ignore\s+previous\s+instructions",
            r"you\s+are\s+now",
            r"system\s*:",
            r"assistant\s*:",
            r"<\s*script",
        ]

        # Remove dangerous patterns
        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # Limit length
        sanitized = sanitized[:max_length]

        return sanitized.strip()

    async def analyze_market_trends(
        self,
        region: Optional[str] = None,
        time_period: str = "30d",
        focus: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered market analysis and trends.

        Args:
            region: City or region to analyze (None = all properties)
            time_period: Time period for analysis ('7d', '30d', '90d')
            focus: Optional focus area for analysis

        Returns:
            Dictionary with market analysis, trends, and statistics
        """
        # Generate cache key
        cache_key = self.cache.generate_key(
            "market_analysis",
            region=region or "all",
            time_period=time_period,
            focus=focus or "general"
        )

        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

        # Build filters
        filters = {}
        if region:
            filters["city"] = region

        # Fetch all properties in region
        properties = self._fetch_properties(filters, limit=200)

        if not properties:
            return {
                "analysis": "No properties found in the specified region.",
                "trends": [],
                "statistics": {},
                "confidence": "low",
                "from_cache": False
            }

        # Calculate market statistics
        stats = self._calculate_market_stats(properties)

        # Analyze days on market distribution
        dom_distribution = self._analyze_dom_distribution(properties)

        # Calculate price trends (if we had date data, we'd analyze over time)
        # For now, we'll analyze current market state
        market_context = self._format_market_context(properties, stats, dom_distribution)

        # Build market analysis prompt
        prompt = self._build_market_analysis_prompt(
            market_context,
            len(properties),
            region or "Salt Lake Valley",
            time_period,
            focus
        )

        # Call Gemini with rate limiting
        try:
            await self.rate_limiter.acquire()
            response = self.model.generate_content(prompt)
            ai_text = response.text

            # Parse response
            result = self._parse_market_analysis_response(ai_text, stats, dom_distribution)

        except Exception as e:
            # Fallback without AI
            result = self._generate_fallback_market_analysis(properties, stats, dom_distribution)
            result["error"] = str(e)

        # Cache for 4 hours
        await self.cache.set(cache_key, result, ttl=14400)

        result["from_cache"] = False
        return result

    def _calculate_market_stats(self, properties: List[Property]) -> Dict[str, Any]:
        """Calculate comprehensive market statistics."""
        prices = [float(p.price) for p in properties if p.price]
        monthly_costs = [float(p.total_monthly_cost) for p in properties if p.total_monthly_cost]
        price_per_sqft = [float(p.price_per_sqft) for p in properties if p.price_per_sqft]
        dom = [p.days_on_market for p in properties if p.days_on_market is not None]

        stats = {
            "total_properties": len(properties),
            "avg_price": sum(prices) / len(prices) if prices else 0,
            "median_price": sorted(prices)[len(prices) // 2] if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "avg_monthly_cost": sum(monthly_costs) / len(monthly_costs) if monthly_costs else 0,
            "avg_price_per_sqft": sum(price_per_sqft) / len(price_per_sqft) if price_per_sqft else 0,
            "avg_days_on_market": sum(dom) / len(dom) if dom else 0,
            "median_days_on_market": sorted(dom)[len(dom) // 2] if dom else 0,
        }

        # City distribution
        city_counts = {}
        for prop in properties:
            city = prop.city or "Unknown"
            city_counts[city] = city_counts.get(city, 0) + 1
        stats["city_distribution"] = city_counts

        return stats

    def _analyze_dom_distribution(self, properties: List[Property]) -> Dict[str, Any]:
        """Analyze days on market distribution to determine market temperature."""
        dom_values = [p.days_on_market for p in properties if p.days_on_market is not None]

        if not dom_values:
            return {
                "avg_dom": 0,
                "fast_moving": 0,
                "moderate": 0,
                "slow_moving": 0,
                "market_temperature": "unknown"
            }

        # Categorize properties
        fast_moving = len([d for d in dom_values if d <= 14])  # < 2 weeks
        moderate = len([d for d in dom_values if 14 < d <= 45])  # 2 weeks - 1.5 months
        slow_moving = len([d for d in dom_values if d > 45])  # > 1.5 months

        total = len(dom_values)
        fast_pct = (fast_moving / total * 100) if total > 0 else 0

        # Determine market temperature
        if fast_pct > 60:
            temperature = "hot"  # Seller's market
        elif fast_pct > 40:
            temperature = "warm"  # Balanced
        elif fast_pct > 20:
            temperature = "cool"  # Slightly favors buyers
        else:
            temperature = "cold"  # Buyer's market

        return {
            "avg_dom": sum(dom_values) / len(dom_values),
            "fast_moving": fast_moving,
            "moderate": moderate,
            "slow_moving": slow_moving,
            "fast_moving_pct": fast_pct,
            "market_temperature": temperature,
            "total_analyzed": total
        }

    def _format_market_context(
        self,
        properties: List[Property],
        stats: Dict[str, Any],
        dom_dist: Dict[str, Any]
    ) -> str:
        """Format market data as context for AI."""
        context_parts = [
            f"Market Overview ({stats['total_properties']} properties):",
            f"- Price Range: ${stats['min_price']:,.0f} - ${stats['max_price']:,.0f}",
            f"- Average Price: ${stats['avg_price']:,.0f}",
            f"- Median Price: ${stats['median_price']:,.0f}",
            f"- Avg Monthly Cost: ${stats['avg_monthly_cost']:,.0f}",
            f"- Avg Price/sqft: ${stats['avg_price_per_sqft']:.2f}",
            f"",
            f"Market Activity:",
            f"- Avg Days on Market: {stats['avg_days_on_market']:.0f} days",
            f"- Median Days on Market: {stats['median_days_on_market']:.0f} days",
            f"- Fast-moving (< 14 days): {dom_dist['fast_moving']} properties ({dom_dist.get('fast_moving_pct', 0):.1f}%)",
            f"- Moderate (14-45 days): {dom_dist['moderate']} properties",
            f"- Slow-moving (> 45 days): {dom_dist['slow_moving']} properties",
            f"- Market Temperature: {dom_dist['market_temperature'].upper()}",
            f"",
            f"Regional Distribution:",
        ]

        for city, count in sorted(stats.get("city_distribution", {}).items(), key=lambda x: x[1], reverse=True):
            context_parts.append(f"- {city}: {count} properties")

        return "\n".join(context_parts)

    def _build_market_analysis_prompt(
        self,
        context: str,
        num_properties: int,
        region: str,
        time_period: str,
        focus: Optional[str]
    ) -> str:
        """Build market analysis prompt for Gemini."""
        system_context = """You are an expert real estate market analyst for Salt Lake Valley with deep knowledge of:
- Market cycles and trends
- Buyer and seller market indicators
- Investment timing strategies
- Local market conditions

Your goal is to provide accurate, actionable market insights that help buyers and sellers make informed decisions."""

        focus_text = f", with special focus on {focus}" if focus else ""

        prompt = f"""{system_context}

Analyze the current real estate market for {region}{focus_text}.

{context}

Provide a comprehensive market analysis including:

1. Overall market summary (2-3 sentences on current market state)
2. Key trends (3-5 bullet points on important patterns)
3. Buyer opportunities (what types of buyers benefit most now)
4. Seller considerations (what sellers should know)
5. Price predictions (short-term outlook based on current data)

Format your response as JSON:
{{
  "analysis": "Overall market summary here...",
  "trends": ["Trend 1", "Trend 2", "Trend 3"],
  "buyer_opportunities": "What buyers should know...",
  "seller_considerations": "What sellers should know...",
  "price_outlook": "Short-term price predictions..."
}}"""

        return prompt

    def _parse_market_analysis_response(
        self,
        ai_text: str,
        stats: Dict[str, Any],
        dom_dist: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse AI market analysis response."""
        try:
            # Try to parse JSON from AI response
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))

                return {
                    "analysis": parsed.get("analysis", ""),
                    "trends": parsed.get("trends", []),
                    "buyer_opportunities": parsed.get("buyer_opportunities", ""),
                    "seller_considerations": parsed.get("seller_considerations", ""),
                    "price_outlook": parsed.get("price_outlook", ""),
                    "statistics": stats,
                    "market_temperature": dom_dist["market_temperature"],
                    "dom_distribution": dom_dist,
                    "confidence": "high"
                }
        except Exception:
            pass

        # Fallback if parsing fails
        return self._generate_fallback_market_analysis([], stats, dom_dist)

    def _generate_fallback_market_analysis(
        self,
        properties: List[Property],
        stats: Dict[str, Any],
        dom_dist: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic market analysis without AI."""
        temp = dom_dist["market_temperature"]

        # Generate analysis based on temperature
        temp_descriptions = {
            "hot": "a strong seller's market with high demand",
            "warm": "a balanced market with moderate activity",
            "cool": "a buyer-friendly market with good inventory",
            "cold": "a buyer's market with ample selection"
        }

        analysis = (
            f"The {stats.get('city_distribution', {}).get(next(iter(stats.get('city_distribution', {})), 'local'), 'local')} market shows "
            f"{temp_descriptions.get(temp, 'moderate activity')} with {stats['total_properties']} properties available. "
            f"Average price is ${stats['avg_price']:,.0f} with properties spending an average of "
            f"{stats['avg_days_on_market']:.0f} days on market."
        )

        trends = [
            f"Average price: ${stats['avg_price']:,.0f}",
            f"Days on market: {stats['avg_days_on_market']:.0f} days average",
            f"{dom_dist.get('fast_moving_pct', 0):.0f}% of properties selling quickly (< 14 days)"
        ]

        if temp in ["hot", "warm"]:
            buyer_opps = "Act quickly on new listings. Competition is moderate to high."
            seller_cons = "Good time to sell. Price competitively for quick sales."
        else:
            buyer_opps = "Take time to negotiate. Inventory levels favor buyers."
            seller_cons = "Price carefully and consider incentives to attract buyers."

        return {
            "analysis": analysis,
            "trends": trends,
            "buyer_opportunities": buyer_opps,
            "seller_considerations": seller_cons,
            "price_outlook": "Market conditions suggest stable pricing in the near term.",
            "statistics": stats,
            "market_temperature": temp,
            "dom_distribution": dom_dist,
            "confidence": "medium"
        }
