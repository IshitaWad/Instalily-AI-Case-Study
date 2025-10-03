#!/usr/bin/env python3
"""
Test the Lead Generation AI Agent with real DeepSeek API
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_client import DeepSeekClient

async def test_deepseek_connection():
    """Test DeepSeek API connection and basic functionality"""
    print("="*60)
    print("Testing DeepSeek API Connection")
    print("="*60)
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key or api_key == 'your_deepseek_api_key_here':
        print("\nERROR: DEEPSEEK_API_KEY not set in .env file")
        print("Please add your API key to the .env file")
        return False
    
    print(f"\nAPI Key found: {api_key[:20]}...")
    
    try:
        # Initialize DeepSeek client
        client = DeepSeekClient(api_key)
        
        # Test 1: Company data enrichment
        print("\n" + "-"*60)
        print("Test 1: Company Data Enrichment")
        print("-"*60)
        
        test_company = {
            'company_name': 'Avery Dennison Graphics Solutions',
            'website': 'https://graphics.averydennison.com',
            'industry': 'Graphics & Signage',
            'revenue_text': '$8.5 billion',
            'employees_text': '10,000+ employees',
            'description': 'Leading manufacturer of graphics and signage materials'
        }
        
        print(f"\nEnriching data for: {test_company['company_name']}")
        enriched = await client.enrich_company_data(test_company)
        
        print("\nEnriched Data:")
        print(f"  Company: {enriched.get('company_name', 'N/A')}")
        print(f"  Estimated Revenue: ${enriched.get('estimated_revenue', 0)/1000000000:.1f}B" if enriched.get('estimated_revenue') else "  Estimated Revenue: N/A")
        print(f"  Strategic Insights: {enriched.get('strategic_insights', 'N/A')[:100]}...")
        
        # Test 2: Decision maker identification
        print("\n" + "-"*60)
        print("Test 2: Decision Maker Identification")
        print("-"*60)
        
        print(f"\nIdentifying decision makers for: {test_company['company_name']}")
        decision_makers = await client.identify_decision_makers(test_company)
        
        print(f"\nFound {len(decision_makers)} decision makers:")
        for i, dm in enumerate(decision_makers, 1):
            print(f"\n  {i}. {dm.get('title', 'N/A')}")
            print(f"     Relevance: {dm.get('relevance', 'N/A')[:80]}...")
        
        # Test 3: Outreach message generation
        print("\n" + "-"*60)
        print("Test 3: Personalized Outreach Generation")
        print("-"*60)
        
        lead_data = {
            'company_name': 'Avery Dennison Graphics Solutions',
            'contact_name': 'Sarah Johnson',
            'contact_title': 'VP of Product Development',
            'industry': 'Graphics & Signage',
            'employees': 10000,
            'qualification_rationale': 'Leading company in graphics solutions with $8.5B revenue'
        }
        
        print(f"\nGenerating outreach for: {lead_data['contact_name']} at {lead_data['company_name']}")
        outreach = await client.generate_outreach_message(lead_data)
        
        print("\nGenerated Outreach Message:")
        print("-" * 60)
        print(outreach)
        print("-" * 60)
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nDeepSeek API is working correctly.")
        print("You can now run the full lead generation system.")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that your API key is correct")
        print("2. Verify you have internet connection")
        print("3. Check DeepSeek API status at https://platform.deepseek.com")
        return False

if __name__ == "__main__":
    print("\nLead Generation AI Agent - API Test")
    print("Testing DeepSeek API integration...\n")
    
    success = asyncio.run(test_deepseek_connection())
    
    if success:
        print("\nNext steps:")
        print("1. Run: python demo.py (for quick demo)")
        print("2. Run: python main.py (to start web server)")
        print("3. Visit: http://localhost:8000/docs (for API interface)")
    else:
        print("\nPlease fix the errors above and try again.")
        sys.exit(1)
