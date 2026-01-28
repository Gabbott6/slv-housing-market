"""
Property scraper service for extracting data from Zillow and Redfin URLs.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class PropertyScraperService:
    """Service for scraping property data from real estate listing URLs."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def scrape_property(self, url: str) -> Dict[str, Any]:
        """
        Scrape property data from a URL.

        Args:
            url: Property listing URL (Zillow or Redfin)

        Returns:
            Dictionary with property data

        Raises:
            ValueError: If URL is invalid or scraping fails
        """
        # Detect which site
        if 'zillow.com' in url.lower():
            return self._scrape_zillow(url)
        elif 'redfin.com' in url.lower():
            return self._scrape_redfin(url)
        else:
            raise ValueError("URL must be from Zillow or Redfin")

    def _scrape_zillow(self, url: str) -> Dict[str, Any]:
        """Scrape property data from Zillow URL."""
        try:
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract property data from Zillow's structure
            property_data = {}

            # Try to find JSON data embedded in the page (Zillow often has this)
            scripts = soup.find_all('script', {'type': 'application/json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # Look for property data in the JSON
                    if isinstance(data, dict):
                        property_data = self._extract_zillow_json_data(data)
                        if property_data:
                            break
                except Exception:
                    continue

            # Fallback: Try to extract from HTML elements
            if not property_data:
                property_data = self._extract_zillow_html_data(soup)

            # Add the URL
            property_data['listing_url'] = url

            # Validate we got at least address and price
            if not property_data.get('address') or not property_data.get('price'):
                raise ValueError("Could not extract required property data (address and price)")

            return property_data

        except requests.RequestException as e:
            logger.error(f"Failed to fetch Zillow URL: {e}")
            raise ValueError(f"Failed to fetch property page: {str(e)}")
        except Exception as e:
            logger.error(f"Error scraping Zillow: {e}")
            raise ValueError(f"Failed to scrape property data: {str(e)}")

    def _extract_zillow_json_data(self, data: Dict) -> Dict[str, Any]:
        """Extract property data from Zillow's JSON structure."""
        property_data = {}

        # Try to navigate the JSON structure
        # Zillow's structure varies, so we need to search recursively
        def search_json(obj, property_data):
            if isinstance(obj, dict):
                # Look for known keys
                if 'address' in obj:
                    addr = obj['address']
                    if isinstance(addr, dict):
                        street = addr.get('streetAddress', '')
                        city = addr.get('city', '')
                        if street:
                            property_data['address'] = street
                        if city:
                            property_data['city'] = city

                if 'price' in obj and not property_data.get('price'):
                    price = obj['price']
                    if isinstance(price, (int, float)):
                        property_data['price'] = price

                if 'bedrooms' in obj and not property_data.get('beds'):
                    property_data['beds'] = obj['bedrooms']

                if 'bathrooms' in obj and not property_data.get('baths'):
                    property_data['baths'] = obj['bathrooms']

                if 'livingArea' in obj and not property_data.get('sqft'):
                    property_data['sqft'] = obj['livingArea']

                if 'resoFacts' in obj:
                    facts = obj['resoFacts']
                    if isinstance(facts, dict):
                        if 'associationFee' in facts:
                            property_data['hoa_fee'] = facts['associationFee']

                # Recurse into nested structures
                for value in obj.values():
                    search_json(value, property_data)

            elif isinstance(obj, list):
                for item in obj:
                    search_json(item, property_data)

        search_json(data, property_data)
        return property_data

    def _extract_zillow_html_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract property data from Zillow HTML elements."""
        property_data = {}

        # Try to find address
        address_elem = soup.find('h1', {'class': re.compile('.*address.*', re.I)})
        if address_elem:
            property_data['address'] = address_elem.get_text(strip=True)

        # Try to find price
        price_elem = soup.find('span', {'data-testid': 'price'})
        if not price_elem:
            price_elem = soup.find('span', string=re.compile(r'\$[\d,]+'))
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'\$?([\d,]+)', price_text)
            if price_match:
                property_data['price'] = float(price_match.group(1).replace(',', ''))

        # Try to find beds/baths/sqft
        facts = soup.find_all('span', {'class': re.compile('.*fact.*', re.I)})
        for fact in facts:
            text = fact.get_text(strip=True).lower()
            if 'bd' in text or 'bed' in text:
                beds_match = re.search(r'(\d+)', text)
                if beds_match:
                    property_data['beds'] = int(beds_match.group(1))
            elif 'ba' in text or 'bath' in text:
                baths_match = re.search(r'([\d.]+)', text)
                if baths_match:
                    property_data['baths'] = float(baths_match.group(1))
            elif 'sqft' in text:
                sqft_match = re.search(r'([\d,]+)', text)
                if sqft_match:
                    property_data['sqft'] = int(sqft_match.group(1).replace(',', ''))

        return property_data

    def _scrape_redfin(self, url: str) -> Dict[str, Any]:
        """Scrape property data from Redfin URL."""
        try:
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            property_data = {}

            # Try to find JSON data (Redfin often has this)
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'SingleFamilyResidence':
                        property_data = self._extract_redfin_json_data(data)
                        break
                except Exception:
                    continue

            # Fallback: Extract from HTML
            if not property_data:
                property_data = self._extract_redfin_html_data(soup)

            # Add the URL
            property_data['listing_url'] = url

            # Validate we got at least address and price
            if not property_data.get('address') or not property_data.get('price'):
                raise ValueError("Could not extract required property data (address and price)")

            return property_data

        except requests.RequestException as e:
            logger.error(f"Failed to fetch Redfin URL: {e}")
            raise ValueError(f"Failed to fetch property page: {str(e)}")
        except Exception as e:
            logger.error(f"Error scraping Redfin: {e}")
            raise ValueError(f"Failed to scrape property data: {str(e)}")

    def _extract_redfin_json_data(self, data: Dict) -> Dict[str, Any]:
        """Extract property data from Redfin's JSON-LD structure."""
        property_data = {}

        # Address
        if 'address' in data:
            addr = data['address']
            if isinstance(addr, dict):
                property_data['address'] = addr.get('streetAddress', '')
                property_data['city'] = addr.get('addressLocality', '')

        # Price
        if 'offers' in data:
            offers = data['offers']
            if isinstance(offers, dict) and 'price' in offers:
                property_data['price'] = float(offers['price'])

        # Features
        if 'numberOfRooms' in data:
            property_data['beds'] = data['numberOfRooms']

        if 'numberOfBathroomsTotal' in data:
            property_data['baths'] = data['numberOfBathroomsTotal']

        if 'floorSize' in data:
            size = data['floorSize']
            if isinstance(size, dict) and 'value' in size:
                property_data['sqft'] = int(size['value'])

        return property_data

    def _extract_redfin_html_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract property data from Redfin HTML elements."""
        property_data = {}

        # Try to find address
        address_elem = soup.find('div', {'class': re.compile('.*street-address.*', re.I)})
        if not address_elem:
            address_elem = soup.find('h1')
        if address_elem:
            property_data['address'] = address_elem.get_text(strip=True)

        # Try to find price
        price_elem = soup.find('div', {'class': re.compile('.*price.*', re.I)})
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'\$?([\d,]+)', price_text)
            if price_match:
                property_data['price'] = float(price_match.group(1).replace(',', ''))

        # Try to find beds/baths/sqft
        stats = soup.find_all('div', {'class': re.compile('.*stat.*', re.I)})
        for stat in stats:
            text = stat.get_text(strip=True).lower()
            if 'bed' in text:
                beds_match = re.search(r'(\d+)', text)
                if beds_match:
                    property_data['beds'] = int(beds_match.group(1))
            elif 'bath' in text:
                baths_match = re.search(r'([\d.]+)', text)
                if baths_match:
                    property_data['baths'] = float(baths_match.group(1))
            elif 'sq' in text or 'sqft' in text:
                sqft_match = re.search(r'([\d,]+)', text)
                if sqft_match:
                    property_data['sqft'] = int(sqft_match.group(1).replace(',', ''))

        return property_data
