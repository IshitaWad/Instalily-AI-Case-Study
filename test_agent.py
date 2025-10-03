#!/usr/bin/env python3
"""
Test script for Lead Generation AI Agent
Demonstrates the application functionality
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LeadGenerationAgent, LeadGenerationRequest
from validation import validate_leads_batch
from dashboard import DashboardGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_lead_generation():
    """Test the lead generation functionality"""
    try:
        # Load environment variables
        load_dotenv()

        # Check if DeepSeek API key is available
        if not os.getenv('DEEPSEEK_API_KEY'):
            logger.warning("DEEPSEEK_API_KEY not found. Please set it in .env file.")
            logger.info("For testing without API key, the app will use fallback data.")
            # Set a dummy API key for testing
            os.environ['DEEPSEEK_API_KEY'] = 'dummy_key_for_testing'

        # Initialize the lead generation agent
        logger.info("Initializing Lead Generation Agent...")
        agent = LeadGenerationAgent()

        # Create test request
        request = LeadGenerationRequest(
            target_industry="Graphics & Signage",
            target_events=["ISA Sign Expo", "SGIA Expo"],
            min_revenue=100000000,  # $100M minimum
            max_results=5  # Limit for demo
        )

        logger.info("Generating leads...")
        leads = await agent.generate_leads(request)

        logger.info(f"Generated {len(leads)} leads")

        # Validate leads
        logger.info("Validating leads...")
        validated_leads = validate_leads_batch(leads)

        # Generate dashboard data
        logger.info("Generating dashboard data...")
        dashboard_data = agent.generate_dashboard_data(validated_leads)

        # Display results
        print("\n" + "="*80)
        print("LEAD GENERATION RESULTS")
        print("="*80)

        # Summary
        summary = dashboard_data['summary']
        print(f"Total Leads: {summary['total_leads']}")
        print(f"Total Estimated Revenue: ${summary['total_estimated_revenue']/1000000000".1f"}B")
        print(f"Average Revenue: ${summary['average_revenue']/1000000".0f"}M")
        print(f"Large Companies: {summary['large_companies']}")
        print(f"Medium Companies: {summary['medium_companies']}")

        print("\n" + "-"*80)
        print("TOP LEADS")
        print("-"*80)

        for i, lead in enumerate(dashboard_data['top_leads'][:3], 1):
            print(f"\n{i}. {lead['company_name']}")
            print(f"   Website: {lead['website']}")
            print(f"   Revenue: ${lead['estimated_revenue']/1000000".0f"}M")
            print(f"   Employees: {lead['employees']}")
            print(f"   Industry: {lead['industry']}")
            print(f"   Rationale: {lead['qualification_rationale']}")

            if lead.get('primary_contact'):
                contact = lead['primary_contact']
                print(f"   Contact: {contact.get('name', 'N/A')} - {contact.get('title', 'N/A')}")
                print(f"   Email: {contact.get('email', 'N/A')}")

            if lead.get('outreach_message'):
                print(f"   Outreach: {lead['outreach_message'][:100]}...")

        # Export sample data
        logger.info("Exporting sample data...")
        dashboard_generator = DashboardGenerator()
        csv_exported = dashboard_generator.export_to_csv(validated_leads, 'sample_leads.csv')
        excel_exported = dashboard_generator.export_to_excel(validated_leads, 'sample_leads.xlsx')

        if csv_exported and excel_exported:
            print("
✅ Sample data exported to:"            print("   - sample_leads.csv")
            print("   - sample_leads.xlsx")

        print("\n" + "="*80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*80)

        # Cleanup
        await agent.scraper.close()

        return True

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return False

async def run_fastapi_server():
    """Run the FastAPI server for testing the web interface"""
    try:
        logger.info("Starting FastAPI server...")
        print("\n🚀 Starting web server at http://localhost:8000")
        print("📊 Dashboard available at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")

        # This would normally start the server
        # For demo purposes, we'll just show the info
        print("\nServer would be running at http://localhost:8000")
        print("API endpoints:")
        print("  - GET  /health")
        print("  - POST /generate-leads")
        print("  - Web interface at /docs")

    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")

if __name__ == "__main__":
    print("🤖 Lead Generation AI Agent - Test Suite")
    print("="*80)

    # Test the lead generation
    success = asyncio.run(test_lead_generation())

    if success:
        print("\n🎉 Ready to run the web application!")
        print("\nTo start the server:")
        print("1. cd lead-generation-agent")
        print("2. pip install -r requirements.txt")
        print("3. Set DEEPSEEK_API_KEY in .env file")
        print("4. python main.py")
        print("\nOr run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n⚠️  Test completed with issues. Check the logs above.")
        sys.exit(1)
