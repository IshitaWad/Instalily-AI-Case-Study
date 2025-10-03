"""
Lead Generation AI Agent for DuPont Tedlar
Automates lead generation, data enrichment, and personalized outreach
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from config import Config
from scraper import WebScraper
from deepseek_client import DeepSeekClient
from lead_processor import LeadProcessor
from dashboard import DashboardGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LeadGenerationRequest:
    """Request model for lead generation"""
    target_industry: str = "Graphics & Signage"
    target_events: List[str] = None
    min_revenue: float = 100000000  # $100M minimum
    max_results: int = 50

@dataclass
class Lead:
    """Lead data structure"""
    company_name: str
    website: str
    revenue: Optional[float] = None
    employees: Optional[int] = None
    industry: str = ""
    decision_makers: List[Dict] = None
    events_attending: List[str] = None
    qualification_rationale: str = ""
    outreach_message: str = ""
    linkedin_profiles: List[str] = None

class LeadGenerationAgent:
    """Main AI agent for lead generation and outreach"""

    def __init__(self):
        self.config = Config()
        self.scraper = WebScraper()
        self.deepseek_client = DeepSeekClient(self.config.deepseek_api_key)
        self.lead_processor = LeadProcessor(self.scraper, self.deepseek_client)
        self.dashboard_generator = DashboardGenerator()

    async def generate_leads(self, request: LeadGenerationRequest) -> List[Lead]:
        """Generate leads based on the request parameters"""
        try:
            logger.info(f"Starting lead generation for {request.target_industry}")

            # Step 1: Research events and associations
            events_data = await self.lead_processor.research_events(request.target_events or [])

            # Step 2: Identify companies from events
            companies = await self.lead_processor.extract_companies_from_events(events_data)

            # Step 3: Filter and prioritize companies
            filtered_companies = await self.lead_processor.filter_companies(
                companies,
                min_revenue=request.min_revenue,
                max_results=request.max_results
            )

            # Step 4: Enrich company data with scraping
            enriched_companies = await self.lead_processor.enrich_company_data(filtered_companies)

            # Step 5: Identify decision makers
            leads_with_contacts = await self.lead_processor.identify_decision_makers(enriched_companies)

            # Step 6: Generate personalized outreach messages
            final_leads = await self.lead_processor.generate_outreach_messages(leads_with_contacts)

            logger.info(f"Generated {len(final_leads)} qualified leads")
            return final_leads

        except Exception as e:
            logger.error(f"Error generating leads: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Lead generation failed: {str(e)}")

    def generate_dashboard_data(self, leads: List[Lead]) -> Dict:
        """Generate dashboard data for visualization"""
        return self.dashboard_generator.create_dashboard(leads)

# FastAPI application
app = FastAPI(
    title="Lead Generation AI Agent",
    description="AI-powered lead generation and outreach for DuPont Tedlar",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the lead generation agent
lead_agent = LeadGenerationAgent()

@app.post("/generate-leads")
async def generate_leads_endpoint(request: dict, background_tasks: BackgroundTasks):
    """Generate leads based on request parameters"""
    try:
        lead_request = LeadGenerationRequest(**request)
        leads = await lead_agent.generate_leads(lead_request)
        dashboard_data = lead_agent.generate_dashboard_data(leads)

        return {
            "status": "success",
            "leads_count": len(leads),
            "leads": leads,
            "dashboard_data": dashboard_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
