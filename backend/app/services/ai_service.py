"""
AI service for housing codes Q&A using Google Gemini API.
Implements RAG (Retrieval-Augmented Generation) for accurate code citations.
"""
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models.housing_code import HousingCode
from ..config import settings


class AIService:
    """AI-powered Q&A service for housing codes and regulations."""

    def __init__(self, db_session: Session, api_key: Optional[str] = None):
        self.db = db_session
        self.api_key = api_key or settings.GOOGLE_API_KEY

        if not self.api_key:
            raise ValueError("Google API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def answer_housing_question(
        self,
        question: str,
        jurisdiction: Optional[str] = None,
        max_context_codes: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question about housing codes using RAG.

        Args:
            question: User's question
            jurisdiction: Optional filter for specific jurisdiction
            max_context_codes: Maximum number of code sections to include in context

        Returns:
            Dictionary with answer and sources
        """
        # Step 1: Search for relevant housing codes
        relevant_codes = self._search_housing_codes(
            question,
            jurisdiction=jurisdiction,
            limit=max_context_codes
        )

        if not relevant_codes:
            return {
                "answer": "I couldn't find any relevant housing codes for your question. The housing codes database may need to be populated with local regulations.",
                "sources": [],
                "confidence": "low"
            }

        # Step 2: Build context from relevant codes
        context = self._format_codes_as_context(relevant_codes)

        # Step 3: Create prompt for Claude
        prompt = self._build_prompt(question, context)

        # Step 4: Call Gemini API
        try:
            response = self.model.generate_content(prompt)
            answer_text = response.text

        except Exception as e:
            return {
                "answer": f"Error calling AI service: {str(e)}",
                "sources": [],
                "confidence": "error"
            }

        # Step 5: Extract sources
        sources = self._extract_sources(relevant_codes)

        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": "high" if len(relevant_codes) >= 2 else "medium",
            "codes_found": len(relevant_codes)
        }

    def _search_housing_codes(
        self,
        query: str,
        jurisdiction: Optional[str] = None,
        limit: int = 5
    ) -> List[HousingCode]:
        """
        Search for relevant housing codes using full-text search.

        Args:
            query: Search query
            jurisdiction: Optional jurisdiction filter
            limit: Maximum number of results

        Returns:
            List of HousingCode instances
        """
        # Build search query
        search_query = self.db.query(HousingCode)

        # Filter by jurisdiction if provided
        if jurisdiction:
            search_query = search_query.filter(
                HousingCode.jurisdiction.ilike(f"%{jurisdiction}%")
            )

        # Full-text search on title and content
        # Use PostgreSQL's to_tsquery for better search
        search_query = search_query.filter(
            func.to_tsvector('english', HousingCode.content).op('@@')(
                func.plainto_tsquery('english', query)
            ) |
            func.to_tsvector('english', HousingCode.title).op('@@')(
                func.plainto_tsquery('english', query)
            )
        )

        # Order by relevance (could use ts_rank here for better ranking)
        results = search_query.limit(limit).all()

        # Fallback: if no results with full-text search, try simple LIKE search
        if not results:
            search_query = self.db.query(HousingCode)
            if jurisdiction:
                search_query = search_query.filter(
                    HousingCode.jurisdiction.ilike(f"%{jurisdiction}%")
                )

            search_query = search_query.filter(
                HousingCode.content.ilike(f"%{query}%") |
                HousingCode.title.ilike(f"%{query}%")
            )

            results = search_query.limit(limit).all()

        return results

    def _format_codes_as_context(self, codes: List[HousingCode]) -> str:
        """Format housing codes as context for Gemini."""
        context_parts = []

        for code in codes:
            context_parts.append(
                f"[{code.code_section}] {code.title}\n"
                f"Jurisdiction: {code.jurisdiction}\n"
                f"Content: {code.content}\n"
                f"Source: {code.source_url}\n"
            )

        return "\n---\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        """Build the prompt for Gemini."""
        prompt = f"""You are an expert assistant for housing codes, building regulations, and local ordinances in Salt Lake Valley.

Context - Relevant Housing Codes and Regulations:
{context}

User Question: {question}

Please provide a clear, accurate answer based on the housing codes provided above. Include:
1. Direct answer to the question
2. Specific code section references (e.g., "According to Section 15.1.2...")
3. Any important caveats or related information
4. Suggestions to consult with local officials if the answer requires professional interpretation

Format your answer in a clear, professional manner suitable for homeowners and developers."""

        return prompt

    def _extract_sources(self, codes: List[HousingCode]) -> List[Dict[str, str]]:
        """Extract source citations from housing codes."""
        sources = []

        for code in codes:
            sources.append({
                "code_section": code.code_section,
                "title": code.title,
                "jurisdiction": code.jurisdiction,
                "source_name": code.source_name or "Housing Code Database",
                "source_url": code.source_url or "",
                "last_updated": code.last_updated.isoformat() if code.last_updated else None
            })

        return sources

    async def add_housing_code(
        self,
        code_section: str,
        title: str,
        content: str,
        jurisdiction: str,
        category: Optional[str] = None,
        source_name: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> HousingCode:
        """
        Add a new housing code to the database.

        Args:
            code_section: Code section identifier
            title: Code title
            content: Full code content
            jurisdiction: Jurisdiction name
            category: Code category
            source_name: Source name
            source_url: Source URL

        Returns:
            Created HousingCode instance
        """
        code = HousingCode(
            code_section=code_section,
            title=title,
            content=content,
            jurisdiction=jurisdiction,
            category=category,
            source_name=source_name,
            source_url=source_url
        )

        self.db.add(code)
        self.db.commit()
        self.db.refresh(code)

        return code
