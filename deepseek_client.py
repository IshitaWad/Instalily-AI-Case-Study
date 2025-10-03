"""
DeepSeek API client for data enrichment and outreach generation
"""

import json
import logging
import re
import httpx
from typing import Dict, List, Optional, Any
import asyncio

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Client for DeepSeek API - OpenAI-compatible interface via OpenRouter"""

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "deepseek/deepseek-chat"
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/dupont-tedlar",
                "X-Title": "DuPont Tedlar Lead Generation"
            },
            timeout=60.0
        )

    def __del__(self):
        self.client.close()

    async def enrich_company_data(self, company_data: Dict) -> Dict:
        """Enrich company data with DeepSeek analysis"""
        try:
            prompt = self._build_enrichment_prompt(company_data)

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a business research analyst specializing in company analysis and market intelligence."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1500
                    }
                )
            )

            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return company_data

            result = response.json()
            enriched_data = self._parse_enrichment_response(result)

            # Merge with original data
            company_data.update(enriched_data)
            return company_data

        except Exception as e:
            logger.error(f"Error enriching company data: {str(e)}")
            return company_data

    async def generate_outreach_message(self, lead_data: Dict) -> str:
        """Generate personalized outreach message"""
        try:
            prompt = self._build_outreach_prompt(lead_data)

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional sales development representative crafting personalized outreach messages for B2B sales."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800
                    }
                )
            )

            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return self._get_fallback_message(lead_data)

            result = response.json()
            message = result["choices"][0]["message"]["content"].strip()

            return message

        except Exception as e:
            logger.error(f"Error generating outreach message: {str(e)}")
            return self._get_fallback_message(lead_data)

    async def identify_decision_makers(self, company_data: Dict) -> List[Dict]:
        """Identify key decision makers for a company"""
        try:
            prompt = self._build_decision_maker_prompt(company_data)

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a sales intelligence specialist identifying key decision makers in B2B companies."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    }
                )
            )

            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return []

            result = response.json()
            decision_makers = self._parse_decision_makers_response(result)

            return decision_makers

        except Exception as e:
            logger.error(f"Error identifying decision makers: {str(e)}")
            return []

    def _build_enrichment_prompt(self, company_data: Dict) -> str:
        """Build prompt for company data enrichment"""
        return f"""
        Analyze the following company information and provide enhanced business intelligence:

        Company: {company_data.get('company_name', 'Unknown')}
        Website: {company_data.get('website', 'Unknown')}
        Industry: {company_data.get('industry', 'Unknown')}
        Current Revenue Data: {company_data.get('revenue_text', 'Not available')}
        Employee Count: {company_data.get('employees_text', 'Not available')}
        Description: {company_data.get('description', 'Not available')}

        Please provide:
        1. Estimated annual revenue (provide a specific dollar amount if possible)
        2. Employee count range or specific number
        3. Key products/services relevant to graphics & signage industry
        4. Market position and competitive advantages
        5. Growth trajectory and recent developments
        6. Strategic priorities and pain points that Tedlar could address

        Focus on aspects relevant to protective films, coatings, and graphics/signage applications.
        Provide specific, actionable insights that would be valuable for sales outreach.
        """

    def _build_outreach_prompt(self, lead_data: Dict) -> str:
        """Build prompt for personalized outreach message"""
        revenue = lead_data.get('estimated_revenue', 0)
        revenue_str = f"${revenue/1000000000:.1f}B" if revenue >= 1000000000 else f"${revenue/1000000:.0f}M" if revenue > 0 else "N/A"
        
        events = lead_data.get('events_attending', [])
        events_str = ", ".join(events[:2]) if events else "industry events"
        
        return f"""
        Create a UNIQUE and personalized LinkedIn outreach message for this specific lead:

        Company: {lead_data.get('company_name', 'Unknown')}
        Revenue: {revenue_str}
        Website: {lead_data.get('website', 'N/A')}
        Decision Maker: {lead_data.get('contact_name', 'Decision Maker')}
        Position: {lead_data.get('contact_title', 'Unknown')}
        Company Industry: {lead_data.get('industry', 'Unknown')}
        Company Size: {lead_data.get('employees', 'Unknown')} employees
        Events They Attend: {events_str}
        Company Description: {lead_data.get('description', 'N/A')}
        Why They're Qualified: {lead_data.get('qualification_rationale', 'Leading company in graphics & signage')}

        IMPORTANT: 
        - Make this message UNIQUE to {lead_data.get('company_name', 'this company')}
        - Reference their specific revenue size ({revenue_str})
        - Mention events they attend if relevant ({events_str})
        - Tailor to their exact position ({lead_data.get('contact_title', 'Unknown')})
        - Make it different from other messages you've generated

        The message should:
        - Be professional and concise (under 150 words)
        - Reference SPECIFIC company details (revenue, events, position)
        - Highlight how DuPont Tedlar's protective films could benefit THEIR specific business
        - Include a clear call-to-action for a brief call or meeting
        - Sound natural and conversational, not sales-y
        - Be UNIQUE - don't use generic templates

        Focus on: Durability, weather resistance, UV protection, and enhanced visual appeal for graphics/signage applications.
        """

    def _build_decision_maker_prompt(self, company_data: Dict) -> str:
        """Build prompt for identifying decision makers"""
        return f"""
        Identify the most relevant decision makers for sales outreach at this company:

        Company: {company_data.get('company_name', 'Unknown')}
        Industry: {company_data.get('industry', 'Graphics & Signage')}
        Website: {company_data.get('website', 'Unknown')}
        Description: {company_data.get('description', 'Not available')}

        For a company in the graphics & signage industry that would benefit from DuPont Tedlar's protective films, identify 2-3 key decision makers who would be involved in:

        1. Product development and material selection
        2. Operations and manufacturing decisions
        3. Innovation and R&D initiatives
        4. Procurement of protective coatings and films

        For each person, provide:
        - Likely job title
        - Department
        - Why they're relevant for Tedlar outreach
        - Key responsibilities that align with protective film applications

        Format as a structured list with specific, realistic job titles.
        """

    def _parse_enrichment_response(self, response: Dict) -> Dict:
        """Parse DeepSeek enrichment response"""
        try:
            content = response["choices"][0]["message"]["content"]

            # Extract structured information from the response
            # This is a simplified parser - in production, you'd use more sophisticated parsing
            enriched_data = {}

            # Look for revenue information
            revenue_match = re.search(r'estimated.*?revenue.*?\$?(\d+(?:\.\d+)?(?:\s*(?:million|billion))?)', content, re.IGNORECASE)
            if revenue_match:
                enriched_data['estimated_revenue'] = self._parse_revenue_value(revenue_match.group(1))

            # Look for employee information
            employee_match = re.search(r'employee.*?(\d+(?:,\d+)*(?:\s*-\s*\d+(?:,\d+)*)?)', content, re.IGNORECASE)
            if employee_match:
                enriched_data['estimated_employees'] = employee_match.group(1)

            # Extract key insights as rationale
            lines = content.split('\n')
            relevant_insights = [line.strip() for line in lines if any(keyword in line.lower() for keyword in ['strategic', 'growth', 'development', 'opportunity', 'benefit', 'advantage'])]
            if relevant_insights:
                enriched_data['strategic_insights'] = ' '.join(relevant_insights[:3])

            return enriched_data

        except Exception as e:
            logger.error(f"Error parsing enrichment response: {str(e)}")
            return {}

    def _parse_decision_makers_response(self, response: Dict) -> List[Dict]:
        """Parse DeepSeek decision makers response"""
        try:
            content = response["choices"][0]["message"]["content"]

            decision_makers = []

            # Split by numbered items or bullet points
            lines = content.split('\n')
            current_person = {}

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for job titles or roles
                if any(title in line.lower() for title in ['vp', 'director', 'manager', 'head of', 'chief']):
                    if current_person:
                        decision_makers.append(current_person)
                    current_person = {'title': line, 'relevance': ''}

                # Look for relevance information
                if 'relevant' in line.lower() or 'responsible' in line.lower() or 'involved' in line.lower():
                    current_person['relevance'] = line

            if current_person:
                decision_makers.append(current_person)

            return decision_makers[:3]  # Limit to top 3

        except Exception as e:
            logger.error(f"Error parsing decision makers response: {str(e)}")
            return []

    def _parse_revenue_value(self, revenue_str: str) -> float:
        """Parse revenue string to numeric value"""
        try:
            # Extract number and multiplier
            parts = revenue_str.lower().split()
            number = float(parts[0])

            if 'billion' in revenue_str:
                return number * 1000000000
            elif 'million' in revenue_str:
                return number * 1000000
            else:
                return number

        except Exception as e:
            logger.error(f"Error parsing revenue value '{revenue_str}': {str(e)}")
            return 0

    def _get_fallback_message(self, lead_data: Dict) -> str:
        """Generate fallback outreach message"""
        company_name = lead_data.get('company_name', 'your company')

        return f"""Hi {lead_data.get('contact_name', 'there')},

I noticed {company_name}'s leadership in the graphics & signage industry. As a {lead_data.get('contact_title', 'decision maker')} there, I thought you might be interested in how DuPont Tedlar's protective films could enhance your product durability and visual appeal.

Would you be open to a brief 15-minute call to explore how Tedlar's weather-resistant and UV-protective properties could benefit your graphics applications?

Best regards,
[Your name]"""

    async def enrich_multiple_companies(self, companies: List[Dict]) -> List[Dict]:
        """Enrich multiple companies concurrently"""
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests

        async def enrich_with_semaphore(company):
            async with semaphore:
                return await self.enrich_company_data(company)

        tasks = [enrich_with_semaphore(company) for company in companies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error enriching company {companies[i]['company_name']}: {str(result)}")
                processed_results.append(companies[i])  # Return original data
            else:
                processed_results.append(result)

        return processed_results
