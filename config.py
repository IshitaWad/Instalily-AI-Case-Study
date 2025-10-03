"""
Configuration settings for the Lead Generation AI Agent
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration class for the lead generation agent"""

    # API Keys
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    linkedin_api_key: Optional[str] = os.getenv("LINKEDIN_API_KEY")
    clay_api_key: Optional[str] = os.getenv("CLAY_API_KEY")

    # Scraping settings
    scraping_timeout: int = 30
    max_concurrent_scrapes: int = 5
    user_agent_rotation: bool = True

    # Data processing
    min_revenue_threshold: float = 100000000  # $100M
    max_companies_per_event: int = 20
    max_decision_makers_per_company: int = 3

    # DeepSeek settings
    deepseek_model: str = "deepseek-chat"
    deepseek_temperature: float = 0.7
    deepseek_max_tokens: int = 2000

    # Dashboard settings
    dashboard_update_interval: int = 300  # 5 minutes

    # Event research
    target_industries: list = None
    event_keywords: list = None

    def __post_init__(self):
        if not self.target_industries:
            self.target_industries = [
                "Graphics & Signage",
                "Large Format Printing",
                "Vehicle Wraps",
                "Architectural Graphics",
                "Sign Manufacturing",
                "Digital Printing",
                "Commercial Printing"
            ]

        if not self.event_keywords:
            self.event_keywords = [
                "ISA Sign Expo",
                "SGIA Expo",
                "Graphics & Signage",
                "Large Format Printing",
                "Vehicle Wrap",
                "Digital Signage Expo",
                "Sign Association",
                "Printing Industry",
                "Graphics Industry"
            ]

    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        if not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required")

        return True
