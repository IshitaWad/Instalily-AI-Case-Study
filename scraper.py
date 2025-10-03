"""
Web scraper for extracting company revenue and employee data
"""

import asyncio
import re
import json
import logging
from typing import Dict, Optional, List
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraper for company data extraction"""

    def __init__(self, config=None):
        self.config = config
        self.ua = UserAgent()
        self.session = None
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def _ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers, timeout=self.timeout)

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()

    async def get_company_data(self, company_name: str, website: str) -> Dict:
        """Extract company data including revenue and employee count"""
        try:
            await self._ensure_session()
            logger.info(f"Scraping data for {company_name} from {website}")

            # Get company overview page
            overview_data = await self._scrape_company_overview(website)

            # Get additional data sources
            linkedin_data = await self._scrape_linkedin(company_name)
            crunchbase_data = await self._scrape_crunchbase(company_name)

            # Combine all data sources
            company_data = {
                'company_name': company_name,
                'website': website,
                'revenue': None,
                'employees': None,
                'industry': '',
                'description': '',
                'founding_year': None,
                'headquarters': '',
                'sources': []
            }

            # Merge data from different sources
            company_data.update(overview_data)
            if linkedin_data:
                company_data.update(linkedin_data)
            if crunchbase_data:
                company_data.update(crunchbase_data)

            return company_data

        except Exception as e:
            logger.error(f"Error scraping {company_name}: {str(e)}")
            return {
                'company_name': company_name,
                'website': website,
                'error': str(e)
            }

    async def _scrape_company_overview(self, website: str) -> Dict:
        """Scrape company overview from their website"""
        try:
            async with self.session.get(website) as response:
                if response.status != 200:
                    return {}

                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')

                data = {}

                # Look for revenue information
                revenue_patterns = [
                    r'\$\d+(?:\.\d+)?\s*(?:million|billion)?\s*(?:in\s*)?revenue',
                    r'revenue.*?\$?\d+(?:\.\d+)?\s*(?:million|billion)',
                    r'\d+(?:\.\d+)?\s*(?:million|billion).*(?:revenue|annual)',
                ]

                for pattern in revenue_patterns:
                    matches = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
                    if matches:
                        data['revenue_text'] = matches[0].strip()
                        break

                # Look for employee information
                employee_patterns = [
                    r'(\d+(?:,\d+)*)\s*employees?',
                    r'employs?\s*(\d+(?:,\d+)*)',
                    r'(\d+(?:,\d+)*)\s*people',
                ]

                for pattern in employee_patterns:
                    matches = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
                    if matches:
                        data['employees_text'] = matches[0].strip()
                        break

                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    data['description'] = meta_desc.get('content', '')[:500]

                return data

        except Exception as e:
            logger.error(f"Error scraping overview for {website}: {str(e)}")
            return {}

    async def _scrape_linkedin(self, company_name: str) -> Dict:
        """Scrape LinkedIn company data"""
        try:
            # This would typically use LinkedIn API, but for demo purposes we'll simulate
            # In production, you'd integrate with LinkedIn Sales Navigator API
            linkedin_url = f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}"

            async with self.session.get(linkedin_url) as response:
                if response.status != 200:
                    return {}

                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')

                data = {}

                # Extract company size and industry from LinkedIn
                # This is a simplified extraction - real implementation would be more sophisticated
                size_match = soup.find(text=re.compile(r'(\d+(?:,\d+)*)\s*employees?', re.IGNORECASE))
                if size_match:
                    data['employees_linkedin'] = size_match.strip()

                return data

        except Exception as e:
            logger.error(f"Error scraping LinkedIn for {company_name}: {str(e)}")
            return {}

    async def _scrape_crunchbase(self, company_name: str) -> Dict:
        """Scrape Crunchbase company data"""
        try:
            # Crunchbase search URL
            search_url = f"https://www.crunchbase.com/search/organizations/field/organizations/name/{company_name.replace(' ', '-')}"

            async with self.session.get(search_url) as response:
                if response.status != 200:
                    return {}

                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')

                data = {}

                # Extract company profile link
                company_link = soup.find('a', href=re.compile(r'/organization/[^/]+$'))
                if company_link:
                    profile_url = f"https://www.crunchbase.com{company_link['href']}"

                    # Get the actual company profile
                    async with self.session.get(profile_url) as profile_response:
                        if profile_response.status == 200:
                            profile_html = await profile_response.text()
                            profile_soup = BeautifulSoup(profile_html, 'lxml')

                            # Extract financial information
                            funding_info = profile_soup.find(text=re.compile(r'revenue|funding|valuation', re.IGNORECASE))
                            if funding_info:
                                data['financial_info'] = funding_info.strip()[:200]

                return data

        except Exception as e:
            logger.error(f"Error scraping Crunchbase for {company_name}: {str(e)}")
            return {}

    def _parse_revenue(self, revenue_text: str) -> Optional[float]:
        """Parse revenue text into numeric value"""
        if not revenue_text:
            return None

        try:
            # Extract numbers and units
            numbers = re.findall(r'\d+(?:\.\d+)?', revenue_text)
            if not numbers:
                return None

            value = float(numbers[0])

            # Handle multipliers
            if 'billion' in revenue_text.lower():
                return value * 1000000000
            elif 'million' in revenue_text.lower():
                return value * 1000000
            elif 'thousand' in revenue_text.lower():
                return value * 1000
            else:
                # Assume it's in dollars if no unit specified
                return value

        except Exception as e:
            logger.error(f"Error parsing revenue '{revenue_text}': {str(e)}")
            return None

    def _parse_employees(self, employees_text: str) -> Optional[int]:
        """Parse employee text into numeric value"""
        if not employees_text:
            return None

        try:
            # Extract numbers
            numbers = re.findall(r'\d+(?:,\d+)*', employees_text)
            if numbers:
                return int(numbers[0].replace(',', ''))
            return None

        except Exception as e:
            logger.error(f"Error parsing employees '{employees_text}': {str(e)}")
            return None

    async def scrape_multiple_companies(self, companies: List[Dict]) -> List[Dict]:
        """Scrape data for multiple companies concurrently"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_scrapes if self.config else 5)

        async def scrape_with_semaphore(company):
            async with semaphore:
                result = await self.get_company_data(company['name'], company['website'])
                # Parse numeric values
                if 'revenue_text' in result:
                    result['revenue'] = self._parse_revenue(result['revenue_text'])
                if 'employees_text' in result:
                    result['employees'] = self._parse_employees(result['employees_text'])
                if 'employees_linkedin' in result:
                    result['employees_linkedin'] = self._parse_employees(result['employees_linkedin'])
                return result

        tasks = [scrape_with_semaphore(company) for company in companies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping company {companies[i]['name']}: {str(result)}")
                processed_results.append({
                    'company_name': companies[i]['name'],
                    'website': companies[i]['website'],
                    'error': str(result)
                })
            else:
                processed_results.append(result)

        return processed_results
