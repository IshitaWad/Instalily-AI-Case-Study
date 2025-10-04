# DuPont Tedlar AI Lead Generation Agent

## Overview  
This documentation outlines an AI agent created for DuPont Tedlar’s Graphics & Signage division to automate lead generation. The system autonomously identifies potential customers at industry events, enriches company profiles with validated data, and generates personalized outreach messages. The primary aim is to reduce manual workload for the sales team while maintaining data accuracy, scalability, and professional communication quality.

## AI Agent Workflow and Architecture  
The AI agent follows a multi-stage automated workflow optimized for accuracy and performance.  

- First, DeepSeek AI identifies relevant trade shows such as the ISA Sign Expo and PRINTING United, building a foundation for subsequent lead discovery.  
- The AI then filters industry-leading companies with revenues exceeding $500 million, prioritizing high-value targets. A strict revenue validation process removes invalid or incomplete records.  
- A dynamic website discovery algorithm locates each company’s websites. The system extracts key data such as descriptions, revenue, and employee counts, augmented by AI-generated strategic insights.  
- The AI identifies relevant executives (VP and Director level) and explains their strategic significance. It is designed to integrate seamlessly with LinkedIn Sales Navigator for live contact data.  
- Context-rich messages are generated referencing validated company details and events. Final outputs are displayed in a dashboard for sales team review and export.  

## Technical Implementation: System Components  
The AI agent is built using a scalable, modular architecture optimized for asynchronous performance and API extensibility.  

- **Frontend:** Streamlit dashboard for user interaction and visualization.  
- **AI Engine:** DeepSeek API via OpenRouter using GPT-4-class reasoning for research and content creation.  
- **Data Collection:** Asynchronous web scraping via aiohttp and BeautifulSoup enables concurrent processing of 20+ companies.  
- **Processing Layer:** Python 3.11+ with async/await for concurrency and performance optimization.  
- **Data Output:** Structured CSV/Excel exports compatible with CRM systems.  
- **Error Handling:** Graceful degradation is implemented through tiered fault recovery and robust API validation.  
- **Scalability:** Rate limiting, modular design, and placeholders for LinkedIn and Clay integrations support enterprise deployment.  

## Data Processing Pipeline  
The pipeline executes in four main stages to maintain accuracy and structure.  

1. AI identifies 5–7 key industry events relevant to the Graphics & Signage sector.  
2. Generates a list of firms with revenues between $500 million and $63 billion. All entries undergo validation and prioritization.  
3. Automated website discovery achieves 85–90% success, followed by AI-based extraction of descriptive and strategic company data.  
4. Decision makers are surfaced with role-based rationales, and AI drafts personalized, company-specific outreach messages designed for direct deployment.  

## Dashboard and User Experience  
The Streamlit dashboard delivers intuitive visualization and operational control:
- **Target Industry Search:** Lets users enter a keyword to define the market focus, which the AI uses to find relevant events and companies.  
- **Number of Leads Slider:** Controls how many leads (up to 20) the system generates at once, balancing between speed and depth of processing.  
- **Generated Company Profiles Include:** Industry fit, revenue, strategic relevance, market activity, decision makers, and outreach drafts.  
- **Dashboard Layout:** List of companies is on the left, detailed info is in the center.  
- **Outreach Drafts:** Generated personalized outreach drafts can also be directly edited/copy-pasted.  
- **Export Options:** One-click export to CSV or Excel files.  
