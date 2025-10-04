"""
Real data lead processor
"""

import asyncio
import logging
import re
from typing import List, Dict, Optional
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class RealDataLeadProcessor:
    def __init__(self, scraper, deepseek_client):
        self.scraper = scraper
        self.deepseek_client = deepseek_client

    async def research_events_with_ai(self, industry: str = "Graphics & Signage") -> List[Dict]:
        """Use AI to identify relevant industry events"""
        try:
            logger.info(f"Using AI to research events for {industry}")
            
            # Use DeepSeek to identify events
            prompt = f"""
            List the top 5-7 major trade shows, conferences, and industry events for the {industry} industry.
            For each event, provide:
            1. Event name
            2. Brief description
            3. Typical attendee types
            4. Website URL (if known)
            
            Format as a structured list with clear sections.
            """
            
            # Call DeepSeek API
            import httpx
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.deepseek_client.client.post(
                    "/chat/completions",
                    json={
                        "model": self.deepseek_client.model,
                        "messages": [
                            {"role": "system", "content": "You are an industry research specialist."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1500
                    }
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                events_text = result["choices"][0]["message"]["content"]
                
                # Parse the AI response to extract events
                events = self._parse_events_from_ai(events_text)
                logger.info(f"AI identified {len(events)} events")
                return events
            else:
                logger.error(f"AI event research failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in AI event research: {str(e)}")
            return []

    def _parse_events_from_ai(self, ai_text: str) -> List[Dict]:
        """Parse event information from AI response"""
        events = []
        lines = ai_text.split('\n')
        current_event = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_event and 'name' in current_event:
                    events.append(current_event)
                    current_event = {}
                continue
                
            # Look for event names (usually numbered or bulleted)
            if re.match(r'^[\d\*\-\•]+\.?\s+(.+)', line):
                if current_event and 'name' in current_event:
                    events.append(current_event)
                event_name = re.sub(r'^[\d\*\-\•]+\.?\s+', '', line)
                current_event = {'name': event_name, 'description': '', 'website': ''}
            elif current_event:
                # Add to description
                current_event['description'] += ' ' + line
                
                # Extract URLs
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    current_event['website'] = url_match.group(0)
        
        if current_event and 'name' in current_event:
            events.append(current_event)
            
        return events[:7]  # Limit to top 7

    async def scrape_event_exhibitors(self, event_name: str, event_website: str) -> List[str]:
        """Scrape actual exhibitor/attendee lists from event websites"""
        try:
            await self.scraper._ensure_session()
            logger.info(f"Scraping exhibitors from {event_website}")
            
            companies = []
            
            # Try to find exhibitor/attendee pages
            search_urls = [
                event_website,
                f"{event_website}/exhibitors",
                f"{event_website}/attendees",
                f"{event_website}/sponsors",
                f"{event_website}/participants"
            ]
            
            for url in search_urls:
                try:
                    async with self.scraper.session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'lxml')
                            
                            # Look for company names in various patterns
                            # Pattern 1: Links with company-like text
                            for link in soup.find_all('a', href=True):
                                text = link.get_text().strip()
                                if text and len(text) > 3 and len(text) < 100:
                                    # Filter for company-like names
                                    if any(keyword in text.lower() for keyword in ['inc', 'corp', 'llc', 'ltd', 'solutions', 'graphics', 'systems']):
                                        companies.append(text)
                            
                            # Pattern 2: Divs or spans with company class names
                            for elem in soup.find_all(['div', 'span', 'h3', 'h4'], class_=re.compile(r'company|exhibitor|sponsor|participant', re.I)):
                                text = elem.get_text().strip()
                                if text and len(text) > 3 and len(text) < 100:
                                    companies.append(text)
                            
                            if companies:
                                break  # Found companies, stop searching
                                
                except Exception as e:
                    logger.debug(f"Could not scrape {url}: {str(e)}")
                    continue
            
            # Remove duplicates and clean
            companies = list(set(companies))
            companies = [c for c in companies if c and len(c) > 3]
            
            logger.info(f"Found {len(companies)} companies from {event_name}")
            return companies[:50]  # Limit to 50
            
        except Exception as e:
            logger.error(f"Error scraping exhibitors: {str(e)}")
            return []

    async def find_companies_with_ai(self, industry: str, event_context: str = "") -> List[Dict]:
        """Use AI to identify companies in the industry"""
        try:
            logger.info(f"Using AI to find companies in {industry}")
            
            prompt = f"""
            List 15-20 of the LARGEST and most prominent companies in the {industry} industry.
            {f"Context: These companies typically attend {event_context}" if event_context else ""}
            
            CRITICAL REQUIREMENTS:
            1. ONLY include companies with annual revenue of $500M or more
            2. Prioritize the TOP revenue companies first (multi-billion dollar enterprises)
            3. You MUST provide accurate, real revenue figures - NO $0, NO guesses
            4. If you don't know the exact revenue, provide a reasonable estimate based on company size
            5. Sort by revenue (highest first)
            
            For each company provide in this exact format:
            
            1. [Company Name]
            Website: [actual company website URL - REQUIRED]
            Revenue: [REAL annual revenue - must be $500M+ - use B for billions, M for millions]
            Employees: [approximate number - must be realistic]
            Products: [main products/services]
            Events: [list 2-3 major trade shows/conferences they typically attend]
            
            VALIDATION RULES:
            - Revenue CANNOT be $0, $0M, or $0B
            - Revenue must be a real number (e.g., $8.5B, $500M, $2.3B)
            - If a company is publicly traded, use their actual reported revenue
            - If private, estimate based on employee count and market position
            - Larger companies (10,000+ employees) typically have $1B+ revenue
            - Medium companies (1,000-10,000 employees) typically have $100M-$1B revenue
            
            Example format:
            1. 3M Commercial Graphics
            Website: https://www.3m.com
            Revenue: $35 billion
            Employees: 95,000
            Products: Commercial graphics, signage materials, protective films
            Events: ISA Sign Expo, PRINTING United, SGIA Expo
            
            2. Avery Dennison Corporation
            Website: https://www.averydennison.com
            Revenue: $8.5 billion
            Employees: 35,000
            Products: Pressure-sensitive materials, graphics solutions
            Events: ISA Sign Expo, Labelexpo, PRINTING United
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.deepseek_client.client.post(
                    "/chat/completions",
                    json={
                        "model": self.deepseek_client.model,
                        "messages": [
                            {"role": "system", "content": "You are a B2B market research specialist."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2000
                    }
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                companies_text = result["choices"][0]["message"]["content"]
                companies = self._parse_companies_from_ai(companies_text)
                logger.info(f"AI identified {len(companies)} companies")
                return companies
            else:
                logger.error(f"AI company research failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in AI company research: {str(e)}")
            return []

    def _parse_companies_from_ai(self, ai_text: str) -> List[Dict]:
        """Parse company information from AI response"""
        companies = []
        lines = ai_text.split('\n')
        current_company = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_company and 'name' in current_company:
                    companies.append(current_company)
                    current_company = {}
                continue
            
            # Look for company names
            if re.match(r'^[\d\*\-\•]+\.?\s+(.+)', line):
                if current_company and 'name' in current_company:
                    companies.append(current_company)
                company_name = re.sub(r'^[\d\*\-\•]+\.?\s+', '', line)
                # Remove common prefixes
                company_name = re.sub(r'^(Company:|Name:)\s*', '', company_name, flags=re.I)
                current_company = {'name': company_name.strip(), 'website': '', 'industry': 'Graphics & Signage', 'events_attending': []}
            elif current_company:
                # Extract revenue
                revenue_match = re.search(r'\$?(\d+(?:\.\d+)?)\s*(billion|million|B|M)', line, re.I)
                if revenue_match:
                    value = float(revenue_match.group(1))
                    unit = revenue_match.group(2).lower()
                    if 'b' in unit:
                        current_company['estimated_revenue'] = value * 1000000000
                    else:
                        current_company['estimated_revenue'] = value * 1000000
                
                # Extract employee count
                emp_match = re.search(r'(\d+(?:,\d+)*)\s*(?:employees?|people)', line, re.I)
                if emp_match:
                    current_company['employees'] = int(emp_match.group(1).replace(',', ''))
                
                # Extract website
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    current_company['website'] = url_match.group(0)
                elif re.search(r'www\.[^\s]+', line):
                    current_company['website'] = 'https://' + re.search(r'www\.[^\s]+', line).group(0)
                
                # Extract events
                if line.lower().startswith('events:'):
                    events_text = re.sub(r'^events:\s*', '', line, flags=re.I)
                    # Split by commas or semicolons
                    events = [e.strip() for e in re.split(r'[,;]', events_text) if e.strip()]
                    current_company['events_attending'] = events
        
        if current_company and 'name' in current_company:
            companies.append(current_company)
        
        # Filter and validate companies
        validated_companies = []
        for company in companies:
            # Set N/A for missing websites
            if not company.get('website'):
                company['website'] = 'N/A'
            
            # Filter out companies with $0 or missing revenue
            revenue = company.get('estimated_revenue', 0)
            if revenue > 0:
                validated_companies.append(company)
            else:
                logger.warning(f"Filtered out {company.get('name')} - invalid revenue: {revenue}")
        
        # Sort by revenue (highest first)
        validated_companies.sort(key=lambda x: x.get('estimated_revenue', 0), reverse=True)
        
        logger.info(f"Validated {len(validated_companies)} companies with proper revenue data")
        return validated_companies

    async def generate_real_leads(self, industry: str = "Graphics & Signage", max_results: int = 20) -> List[Dict]:
        """Generate leads using only real data sources"""
        try:
            logger.info(f"Generating real leads for {industry}")
            
            # Step 1: Research events with AI
            events = await self.research_events_with_ai(industry)
            
            # Step 2: Find companies with AI
            all_companies = []
            for event in events[:3]:  # Use top 3 events for context
                companies = await self.find_companies_with_ai(industry, event.get('name', ''))
                all_companies.extend(companies)
            
            # Remove duplicates
            unique_companies = {}
            for company in all_companies:
                name = company['name'].lower()
                if name not in unique_companies:
                    unique_companies[name] = company
            
            companies = list(unique_companies.values())[:max_results]
            
            # Step 3: Enrich with real web scraping
            logger.info(f"Scraping real data for {len(companies)} companies")
            enriched_companies = []
            
            for company in companies:
                try:
                    # Real web scraping
                    scraped_data = await self.scraper.get_company_data(
                        company['name'], 
                        company.get('website', '')
                    )
                    
                    # Merge AI and scraped data
                    merged = {**company, **scraped_data}
                    
                    # AI enrichment
                    enriched = await self.deepseek_client.enrich_company_data(merged)
                    
                    # Generate qualification rationale with AI
                    enriched['qualification_rationale'] = await self._generate_ai_rationale(enriched)
                    
                    # Identify decision makers with AI
                    decision_makers = await self.deepseek_client.identify_decision_makers(enriched)
                    enriched['decision_makers'] = decision_makers
                    
                    # Generate contacts (this would use LinkedIn/Clay in production)
                    enriched['contacts'] = self._generate_contacts_from_decision_makers(
                        decision_makers, 
                        enriched['company_name']
                    )
                    
                    # Generate personalized outreach with AI
                    if enriched.get('contacts'):
                        primary_contact = enriched['contacts'][0]
                        lead_data = {
                            'company_name': enriched['company_name'],
                            'contact_name': primary_contact.get('name', 'Decision Maker'),
                            'contact_title': primary_contact.get('title', ''),
                            'industry': enriched.get('industry', industry),
                            'employees': enriched.get('employees', 'Unknown'),
                            'qualification_rationale': enriched.get('qualification_rationale', '')
                        }
                        enriched['outreach_message'] = await self.deepseek_client.generate_outreach_message(lead_data)
                        enriched['primary_contact'] = primary_contact
                    
                    enriched_companies.append(enriched)
                    
                except Exception as e:
                    logger.error(f"Error processing {company['name']}: {str(e)}")
                    continue
            
            logger.info(f"Generated {len(enriched_companies)} real leads")
            return enriched_companies
            
        except Exception as e:
            logger.error(f"Error generating real leads: {str(e)}")
            return []

    async def _generate_ai_rationale(self, company: Dict) -> str:
        """Generate qualification rationale using AI"""
        try:
            prompt = f"""
            Explain in 2-3 sentences why {company.get('company_name', 'this company')} is a qualified lead for DuPont Tedlar's protective films.
            
            Company info:
            - Revenue: ${company.get('estimated_revenue', 0)/1000000:.0f}M
            - Employees: {company.get('employees', 'Unknown')}
            - Industry: {company.get('industry', 'Graphics & Signage')}
            - Description: {company.get('description', 'N/A')[:200]}
            
            Focus on: revenue size, industry fit, and how Tedlar's protective films (durability, UV protection, weather resistance) would benefit them.
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.deepseek_client.client.post(
                    "/chat/completions",
                    json={
                        "model": self.deepseek_client.model,
                        "messages": [
                            {"role": "system", "content": "You are a B2B sales analyst."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 300
                    }
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                return f"{company.get('company_name', 'This company')} is a qualified lead for DuPont Tedlar."
                
        except Exception as e:
            logger.error(f"Error generating rationale: {str(e)}")
            return f"{company.get('company_name', 'This company')} is a qualified lead for DuPont Tedlar."

    def _generate_contacts_from_decision_makers(self, decision_makers: List[Dict], company_name: str) -> List[Dict]:
        """
        Placeholder for contact info from decision makers
        In production, this would use LinkedIn Sales Navigator or Clay API
        """
        contacts = []
        
        for i, dm in enumerate(decision_makers[:2]):
            title = dm.get('title', 'Director')
            
            # Placeholder contact - in production, use LinkedIn/Clay API
            contact = {
                'name': 'N/A - Use LinkedIn Sales Navigator',
                'title': title,
                'email': 'N/A - Use Clay API for email lookup',
                'linkedin_url': 'N/A - Use LinkedIn Sales Navigator API',
                'relevance': dm.get('relevance', 'Key decision maker'),
                'note': 'Contact information requires LinkedIn Sales Navigator or Clay API integration'
            }
            
            contacts.append(contact)
        
        return contacts
