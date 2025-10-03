#!/usr/bin/env python3
"""
Simple demo of the Lead Generation AI Agent
Shows basic functionality without external API calls
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor
from dashboard import DashboardGenerator
from validation import validate_leads_batch

class MockScraper:
    """Mock scraper for demo purposes"""

    async def scrape_multiple_companies(self, companies):
        # Return mock data for demo
        return [
            {
                'company_name': company['name'],
                'website': company['website'],
                'estimated_revenue': 500000000,
                'employees': '1,000+',
                'industry': 'Graphics & Signage'
            }
            for company in companies
        ]

class MockDeepSeekClient:
    """Mock DeepSeek client for demo purposes"""

    async def enrich_multiple_companies(self, companies):
        for company in companies:
            company['qualification_rationale'] = f"{company['company_name']} is a leading company in the graphics & signage industry with significant market presence and growth potential."
        return companies

    async def identify_decision_makers(self, company):
        return [
            {'title': 'VP of Product Development', 'relevance': 'Key decision maker for material selection'},
            {'title': 'Director of Operations', 'relevance': 'Oversees manufacturing and quality'}
        ]

    async def generate_outreach_message(self, lead_data):
        return f"Hi {lead_data.get('contact_name', 'there')}, I noticed {lead_data.get('company_name', 'your company')}'s leadership in graphics solutions. As {lead_data.get('contact_title', 'a decision maker')} there, I thought you might be interested in how DuPont Tedlar's protective films could enhance your product durability and visual appeal. Would you be open to a brief 15-minute call? Best regards, [Your name]"

async def demo():
    """Run a demo of the lead generation system"""
    print("Lead Generation AI Agent - Demo")
    print("=" * 50)

    # Mock components
    scraper = MockScraper()
    deepseek_client = MockDeepSeekClient()

    # Initialize lead processor
    processor = LeadProcessor(scraper, deepseek_client)

    # Sample companies
    sample_companies = [
        {'name': 'Avery Dennison Graphics Solutions', 'website': 'https://graphics.averydennison.com'},
        {'name': '3M Commercial Graphics', 'website': 'https://www.3m.com/graphics'},
        {'name': 'Arlon Graphics', 'website': 'https://www.arlon.com'}
    ]

    print(f"Processing {len(sample_companies)} sample companies...")

    # Process the leads
    enriched_companies = await processor.enrich_company_data(sample_companies)
    companies_with_contacts = await processor.identify_decision_makers(enriched_companies)
    final_leads = await processor.generate_outreach_messages(companies_with_contacts)

    # Validate leads
    validated_leads = validate_leads_batch(final_leads)

    # Generate dashboard
    dashboard_gen = DashboardGenerator()
    dashboard_data = dashboard_gen.create_dashboard(validated_leads)

    print("Lead generation completed!")
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)

    summary = dashboard_data['summary']
    print(f"Total Leads Generated: {summary['total_leads']}")
    print(f"Total Revenue: ${summary['total_estimated_revenue']/1000000000:.1f}B")
    print(f"Average Revenue: ${summary['average_revenue']/1000000:.0f}M")

    print("\n" + "-" * 50)
    print("TOP LEADS")
    print("-" * 50)

    for i, lead in enumerate(dashboard_data['top_leads'][:3], 1):
        print(f"\n{i}. {lead['company_name']}")
        print(f"   Revenue: ${lead['estimated_revenue']/1000000:.0f}M")
        print(f"   Employees: {lead['employees']}")
        print(f"   Industry: {lead['industry']}")
        print(f"   Rationale: {lead['qualification_rationale'][:100]}...")

        if lead.get('primary_contact'):
            contact = lead['primary_contact']
            print(f"   Contact: {contact.get('name', 'N/A')}")
            print(f"   Email: {contact.get('email', 'N/A')}")

        if lead.get('outreach_message'):
            print(f"   Message: {lead['outreach_message'][:80]}...")

    print("\n" + "=" * 50)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\nTo run the full application:")
    print("1. Set DEEPSEEK_API_KEY in .env file")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run: python main.py")
    print("4. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(demo())
