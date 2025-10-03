"""
Lead processor for coordinating data collection and enrichment
"""

import asyncio
import logging
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import json

logger = logging.getLogger(__name__)

class LeadProcessor:
    """Coordinates lead generation, data enrichment, and outreach"""

    def __init__(self, scraper, deepseek_client):
        self.scraper = scraper
        self.deepseek_client = deepseek_client

    async def research_events(self, target_events: List[str] = None) -> List[Dict]:
        """Research relevant industry events and associations"""
        try:
            logger.info("Researching industry events and associations")

            # Default events if none provided
            if not target_events:
                target_events = [
                    "ISA Sign Expo",
                    "SGIA Expo",
                    "Graphics & Signage Trade Show",
                    "Large Format Printing Conference",
                    "Digital Signage Expo",
                    "Sign Association Annual Meeting"
                ]

            events_data = []

            for event in target_events:
                # Search for event information
                event_info = await self._search_event_info(event)
                if event_info:
                    events_data.append(event_info)

            return events_data

        except Exception as e:
            logger.error(f"Error researching events: {str(e)}")
            return []

    async def _search_event_info(self, event_name: str) -> Dict:
        """Search for event information"""
        # This would typically involve web searches or API calls
        # For demo purposes, we'll return structured mock data
        mock_events = {
            "ISA Sign Expo": {
                "name": "ISA Sign Expo",
                "description": "International Sign Association's premier trade show for signage professionals",
                "frequency": "Annual",
                "typical_attendees": ["Sign companies", "Graphics professionals", "Large format printers"],
                "companies": [
                    "Avery Dennison Graphics Solutions",
                    "3M Commercial Graphics",
                    "Arlon Graphics",
                    "FDC Graphic Films",
                    "Mactac Graphics"
                ]
            },
            "SGIA Expo": {
                "name": "SGIA Expo",
                "description": "Specialty Graphics Imaging Association's flagship event",
                "frequency": "Annual",
                "typical_attendees": ["Digital printers", "Screen printers", "Graphics producers"],
                "companies": [
                    "Canon Solutions America",
                    "EFI",
                    "HP Graphics",
                    "Mimaki USA",
                    "Roland DGA"
                ]
            }
        }

        return mock_events.get(event_name, {
            "name": event_name,
            "description": "Industry event for graphics and signage professionals",
            "companies": []
        })

    async def extract_companies_from_events(self, events_data: List[Dict]) -> List[Dict]:
        """Extract companies from event data"""
        companies = []

        for event in events_data:
            event_companies = event.get('companies', [])

            for company_name in event_companies:
                # Create company entry with website lookup
                website = await self._find_company_website(company_name)

                company = {
                    'name': company_name,
                    'website': website,
                    'source_event': event.get('name', 'Unknown'),
                    'industry': 'Graphics & Signage',
                    'events_attending': [event.get('name', 'Unknown')]
                }

                companies.append(company)

        # Remove duplicates and limit results
        unique_companies = self._deduplicate_companies(companies)

        logger.info(f"Extracted {len(unique_companies)} companies from events")
        return unique_companies[:50]  # Limit for demo

    async def _find_company_website(self, company_name: str) -> str:
        """Find company website"""
        # This would typically involve web searches or API calls
        # For demo purposes, we'll use a simple mapping
        website_mapping = {
            "Avery Dennison Graphics Solutions": "https://graphics.averydennison.com",
            "3M Commercial Graphics": "https://www.3m.com/graphics",
            "Arlon Graphics": "https://www.arlon.com",
            "FDC Graphic Films": "https://www.fdcfilms.com",
            "Mactac Graphics": "https://www.mactac.com/graphics",
            "Canon Solutions America": "https://csa.canon.com",
            "EFI": "https://www.efi.com",
            "HP Graphics": "https://www.hp.com/graphics",
            "Mimaki USA": "https://www.mimakiusa.com",
            "Roland DGA": "https://www.rolanddga.com"
        }

        # Only return if in mapping, otherwise N/A - DO NOT GENERATE
        return website_mapping.get(company_name, 'N/A')

    def _deduplicate_companies(self, companies: List[Dict]) -> List[Dict]:
        """Remove duplicate companies"""
        seen = set()
        unique = []

        for company in companies:
            company_key = company['name'].lower()
            if company_key not in seen:
                seen.add(company_key)
                unique.append(company)

        return unique

    async def filter_companies(self, companies: List[Dict], min_revenue: float = 100000000, max_results: int = 50) -> List[Dict]:
        """Filter companies by revenue and size criteria"""
        logger.info(f"Filtering {len(companies)} companies by revenue threshold ${min_revenue/1000000}M")

        # In a real implementation, this would use the scraped revenue data
        # For demo purposes, we'll assign mock revenue data based on company size
        filtered_companies = []

        for company in companies:
            # Mock revenue assignment based on company type
            mock_revenue = self._assign_mock_revenue(company['name'])

            if mock_revenue >= min_revenue:
                company['estimated_revenue'] = mock_revenue
                filtered_companies.append(company)

        # Sort by revenue descending
        filtered_companies.sort(key=lambda x: x.get('estimated_revenue', 0), reverse=True)

        logger.info(f"Filtered to {len(filtered_companies)} companies meeting revenue criteria")
        return filtered_companies[:max_results]

    def _assign_mock_revenue(self, company_name: str) -> float:
        """Assign mock revenue data for demo purposes"""
        # Large established companies
        large_companies = {
            "Avery Dennison Graphics Solutions": 8500000000,  # $8.5B
            "3M Commercial Graphics": 35000000000,  # $35B (3M total)
            "Canon Solutions America": 4500000000,  # $4.5B
            "HP Graphics": 63000000000,  # $63B (HP total)
        }

        return large_companies.get(company_name, 500000000)  # Default $500M for others

    async def enrich_company_data(self, companies: List[Dict]) -> List[Dict]:
        """Enrich company data using scraping and DeepSeek"""
        logger.info(f"Enriching data for {len(companies)} companies")

        # Step 1: Scrape basic company data
        scraped_data = await self.scraper.scrape_multiple_companies(companies)

        # Step 2: Enrich with DeepSeek analysis
        enriched_data = await self.deepseek_client.enrich_multiple_companies(scraped_data)

        # Step 3: Generate qualification rationale
        for company in enriched_data:
            company['qualification_rationale'] = self._generate_qualification_rationale(company)

        return enriched_data

    def _generate_qualification_rationale(self, company: Dict) -> str:
        """Generate rationale for why this company is a qualified lead"""
        name = company.get('company_name', 'Unknown')
        revenue = company.get('estimated_revenue', 0)
        employees = company.get('employees', 'Unknown')

        rationale = f"{name} is a qualified lead for DuPont Tedlar because: "

        # Revenue qualification
        if revenue >= 1000000000:  # $1B+
            rationale += f"it's a large enterprise with ${revenue/1000000000:.1f}B+ in annual revenue, "
        elif revenue >= 100000000:  # $100M+
            rationale += f"it's a mid-to-large company with ${revenue/1000000:.0f}M+ in annual revenue, "

        # Industry fit
        rationale += "it specializes in graphics & signage solutions where Tedlar's protective films provide significant value through enhanced durability, UV protection, and weather resistance. "

        # Market position
        if employees and isinstance(employees, int) and employees > 1000:
            rationale += f"With {employees:,}+ employees, it has the scale to benefit from Tedlar's enterprise-grade protective solutions."

        return rationale.strip()

    async def identify_decision_makers(self, companies: List[Dict]) -> List[Dict]:
        """Identify key decision makers for each company"""
        logger.info(f"Identifying decision makers for {len(companies)} companies")

        enriched_companies = []

        for company in companies:
            # Use DeepSeek to identify relevant decision makers
            decision_makers = await self.deepseek_client.identify_decision_makers(company)

            # Add decision makers to company data
            company['decision_makers'] = decision_makers

            # Generate mock contact information for demo
            company['contacts'] = self._generate_mock_contacts(decision_makers, company['company_name'])

            enriched_companies.append(company)

        return enriched_companies

    def _generate_mock_contacts(self, decision_makers: List[Dict], company_name: str) -> List[Dict]:
        """Generate mock contact information for demo purposes"""
        contacts = []

        for i, dm in enumerate(decision_makers[:2]):  # Max 2 per company
            title = dm.get('title', 'Director')

            # Generate realistic name based on title and company
            if 'VP' in title:
                first_name = "Sarah" if i % 2 == 0 else "Michael"
            elif 'Director' in title:
                first_name = "Jennifer" if i % 2 == 0 else "David"
            else:
                first_name = "Lisa" if i % 2 == 0 else "Robert"

            last_name = company_name.split()[0] if company_name.split() else "Smith"

            # Create proper email domain from company name
            domain = company_name.lower()
            # Remove common suffixes
            domain = re.sub(r'\s+(graphics|solutions|films|inc|corp|llc|ltd|america|usa).*$', '', domain)
            # Clean for domain
            domain = domain.replace(' & ', '').replace(' ', '').replace('&', '')
            domain = re.sub(r'[^a-z0-9]', '', domain)
            
            # Create LinkedIn-friendly slug
            linkedin_slug = company_name.lower()
            linkedin_slug = re.sub(r'\s+(graphics|solutions|films).*$', '', linkedin_slug)
            linkedin_slug = linkedin_slug.replace(' & ', '-').replace(' ', '-').replace('&', 'and')
            linkedin_slug = re.sub(r'[^a-z0-9-]', '', linkedin_slug)

            contact = {
                'name': f"{first_name} {last_name}",
                'title': title,
                'email': f"{first_name.lower()}.{last_name.lower()}@{domain}.com",
                'linkedin_url': f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{linkedin_slug}/",
                'relevance': dm.get('relevance', 'Key decision maker for material selection and product development')
            }

            contacts.append(contact)

        return contacts

    async def generate_outreach_messages(self, companies: List[Dict]) -> List[Dict]:
        """Generate personalized outreach messages for each lead"""
        logger.info(f"Generating outreach messages for {len(companies)} companies")

        final_leads = []

        for company in companies:
            # Generate message for primary contact
            primary_contact = company.get('contacts', [{}])[0] if company.get('contacts') else {}

            if primary_contact:
                lead_data = {
                    'company_name': company.get('company_name', ''),
                    'contact_name': primary_contact.get('name', 'Decision Maker'),
                    'contact_title': primary_contact.get('title', ''),
                    'industry': company.get('industry', ''),
                    'employees': company.get('employees', 'Unknown'),
                    'estimated_revenue': company.get('estimated_revenue', 0),
                    'website': company.get('website', ''),
                    'events_attending': company.get('events_attending', []),
                    'description': company.get('description', ''),
                    'qualification_rationale': company.get('qualification_rationale', '')
                }

                # Generate personalized message
                outreach_message = await self.deepseek_client.generate_outreach_message(lead_data)

                company['outreach_message'] = outreach_message
                company['primary_contact'] = primary_contact

            final_leads.append(company)

        return final_leads
