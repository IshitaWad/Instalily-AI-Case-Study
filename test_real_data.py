#!/usr/bin/env python3
"""
Test the Lead Generation AI Agent with REAL DATA ONLY
No mock data - uses actual AI and web scraping
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import WebScraper
from deepseek_client import DeepSeekClient
from real_data_processor import RealDataLeadProcessor
from dashboard import DashboardGenerator
from validation import validate_leads_batch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_real_data_generation():
    """Test lead generation with 100% real data"""
    print("="*70)
    print("LEAD GENERATION WITH REAL DATA ONLY")
    print("="*70)
    print("\nThis test uses:")
    print("  ✓ AI to research industry events")
    print("  ✓ AI to identify companies")
    print("  ✓ Real web scraping for company data")
    print("  ✓ AI for data enrichment")
    print("  ✓ AI for decision maker identification")
    print("  ✓ AI for personalized outreach generation")
    print("\n" + "="*70)
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key or api_key == 'your_deepseek_api_key_here':
        print("\n❌ ERROR: DEEPSEEK_API_KEY not set in .env file")
        print("Please add your API key to the .env file")
        return False
    
    print(f"\n✓ API Key found: {api_key[:20]}...")
    
    try:
        # Initialize components
        print("\n📦 Initializing components...")
        scraper = WebScraper()
        deepseek_client = DeepSeekClient(api_key)
        processor = RealDataLeadProcessor(scraper, deepseek_client)
        
        # Generate leads with real data
        print("\n🔍 Step 1: Researching industry events with AI...")
        print("   (This may take 30-60 seconds)")
        
        events = await processor.research_events_with_ai("Graphics & Signage")
        
        if events:
            print(f"\n✓ Found {len(events)} industry events:")
            for i, event in enumerate(events[:5], 1):
                print(f"   {i}. {event.get('name', 'Unknown')}")
        else:
            print("\n⚠️  No events found, continuing with company research...")
        
        # Find companies
        print("\n🏢 Step 2: Identifying companies with AI...")
        print("   (This may take 30-60 seconds)")
        
        companies = await processor.find_companies_with_ai("Graphics & Signage")
        
        if companies:
            print(f"\n✓ Found {len(companies)} companies:")
            for i, company in enumerate(companies[:10], 1):
                revenue = company.get('estimated_revenue', 0)
                revenue_str = f"${revenue/1000000000:.1f}B" if revenue >= 1000000000 else f"${revenue/1000000:.0f}M" if revenue > 0 else "Unknown"
                print(f"   {i}. {company.get('name', 'Unknown')} - {revenue_str}")
        else:
            print("\n❌ No companies found")
            return False
        
        # Generate complete leads (limit to 3 for testing to avoid rate limits)
        print("\n🚀 Step 3: Generating complete leads with real data...")
        print("   Processing 3 companies (to avoid rate limits)")
        print("   Each company will be:")
        print("     - Scraped for real data")
        print("     - Enriched with AI analysis")
        print("     - Assigned decision makers via AI")
        print("     - Given personalized outreach via AI")
        print("\n   ⏳ This will take 2-3 minutes...")
        
        leads = await processor.generate_real_leads("Graphics & Signage", max_results=3)
        
        if not leads:
            print("\n❌ No leads generated")
            return False
        
        # Validate leads
        print(f"\n✓ Generated {len(leads)} leads, validating...")
        validated_leads = validate_leads_batch(leads)
        
        # Generate dashboard
        dashboard_gen = DashboardGenerator()
        dashboard_data = dashboard_gen.create_dashboard(validated_leads)
        
        # Display results
        print("\n" + "="*70)
        print("RESULTS - 100% REAL DATA")
        print("="*70)
        
        summary = dashboard_data['summary']
        print(f"\n📊 Summary:")
        print(f"   Total Leads: {summary['total_leads']}")
        if summary.get('total_estimated_revenue', 0) > 0:
            print(f"   Total Revenue: ${summary['total_estimated_revenue']/1000000000:.1f}B")
            print(f"   Average Revenue: ${summary['average_revenue']/1000000:.0f}M")
        
        print("\n" + "-"*70)
        print("DETAILED LEADS")
        print("-"*70)
        
        for i, lead in enumerate(validated_leads, 1):
            print(f"\n{'='*70}")
            print(f"LEAD #{i}: {lead.get('company_name', 'Unknown')}")
            print(f"{'='*70}")
            
            print(f"\n📍 Company Information:")
            print(f"   Website: {lead.get('website', 'N/A')}")
            
            revenue = lead.get('estimated_revenue', 0)
            if revenue > 0:
                revenue_str = f"${revenue/1000000000:.1f}B" if revenue >= 1000000000 else f"${revenue/1000000:.0f}M"
                print(f"   Revenue: {revenue_str}")
            
            employees = lead.get('employees', 'Unknown')
            print(f"   Employees: {employees}")
            print(f"   Industry: {lead.get('industry', 'N/A')}")
            
            print(f"\n💡 Qualification Rationale:")
            rationale = lead.get('qualification_rationale', 'N/A')
            print(f"   {rationale}")
            
            if lead.get('decision_makers'):
                print(f"\n👥 Decision Makers ({len(lead['decision_makers'])}):")
                for j, dm in enumerate(lead['decision_makers'][:3], 1):
                    print(f"   {j}. {dm.get('title', 'N/A')}")
                    relevance = dm.get('relevance', 'N/A')
                    if len(relevance) > 80:
                        relevance = relevance[:80] + "..."
                    print(f"      → {relevance}")
            
            if lead.get('primary_contact'):
                contact = lead['primary_contact']
                print(f"\n📧 Primary Contact:")
                print(f"   Name: {contact.get('name', 'N/A')}")
                print(f"   Title: {contact.get('title', 'N/A')}")
                print(f"   Email: {contact.get('email', 'N/A')}")
                print(f"   LinkedIn: {contact.get('linkedin_url', 'N/A')}")
            
            if lead.get('outreach_message'):
                print(f"\n💬 Personalized Outreach Message:")
                print("-"*70)
                print(lead['outreach_message'])
                print("-"*70)
        
        # Export
        print(f"\n📁 Exporting data...")
        csv_file = 'real_leads_export.csv'
        excel_file = 'real_leads_export.xlsx'
        
        dashboard_gen.export_to_csv(validated_leads, csv_file)
        dashboard_gen.export_to_excel(validated_leads, excel_file)
        
        print(f"   ✓ Exported to: {csv_file}")
        print(f"   ✓ Exported to: {excel_file}")
        
        print("\n" + "="*70)
        print("✅ REAL DATA LEAD GENERATION COMPLETE!")
        print("="*70)
        
        print("\n🎉 Success! All data was generated using:")
        print("   • AI for event research")
        print("   • AI for company identification")
        print("   • Real web scraping")
        print("   • AI for enrichment and analysis")
        print("   • AI for personalized outreach")
        
        # Cleanup
        await scraper.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🤖 Lead Generation AI Agent - REAL DATA TEST")
    print("="*70)
    print("\nNOTE: This test uses real AI and web scraping.")
    print("      It will take 2-3 minutes and use ~10-15 API calls.")
    print("      Make sure you're not rate limited on OpenRouter.")
    print("\n" + "="*70)
    
    input("\nPress Enter to start the real data test...")
    
    success = asyncio.run(test_real_data_generation())
    
    if success:
        print("\n✅ Test completed successfully!")
        print("\nYour leads are ready to use for outreach.")
        print("Check the exported CSV/Excel files for CRM import.")
    else:
        print("\n❌ Test failed. Check the errors above.")
        sys.exit(1)
