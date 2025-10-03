# Lead Generation AI Agent for DuPont Tedlar

## Overview

An AI-powered lead generation and outreach automation system designed for DuPont Tedlar's Graphics & Signage team. This agent automatically identifies qualified leads, enriches company data, and generates personalized outreach messages.

## Features

✅ **Automated Lead Generation** - Identifies companies from industry events and associations
✅ **Real-time Data Scraping** - Extracts revenue, employee count, and company information
✅ **AI-Powered Enrichment** - Uses DeepSeek AI for data enrichment and market analysis
✅ **Persona Identification** - Identifies key decision makers (VP, Director, etc.)
✅ **Personalized Outreach** - Generates tailored LinkedIn messages
✅ **Dashboard & Analytics** - Visual reports and export capabilities
✅ **API Integrations** - Provisions for LinkedIn Sales Navigator and Clay API

## Quick Start

### 1. Installation

```bash
cd lead-generation-agent
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env file with your API keys
```

**Required:**
- `DEEPSEEK_API_KEY` - Your DeepSeek API key

**Optional:**
- `LINKEDIN_API_KEY` - LinkedIn Sales Navigator API key
- `LINKEDIN_ACCESS_TOKEN` - LinkedIn access token
- `CLAY_API_KEY` - Clay API key

### 3. Run the Application

```bash
# Start the web server
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the System

```bash
python test_agent.py
```

## API Usage

### Generate Leads

```bash
curl -X POST "http://localhost:8000/generate-leads" \
  -H "Content-Type: application/json" \
  -d '{
    "target_industry": "Graphics & Signage",
    "target_events": ["ISA Sign Expo", "SGIA Expo"],
    "min_revenue": 100000000,
    "max_results": 50
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Scraper   │───▶│  Lead Processor  │───▶│  DeepSeek AI    │
│                 │    │                  │    │                 │
│ • Company data  │    │ • Event research │    │ • Data enrich   │
│ • Revenue/emp   │    │ • Company filter │    │ • Outreach gen  │
│ • Real-time     │    │ • Persona ID     │    │ • Market intel  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Validation    │    │   Dashboard      │    │   Export        │
│                 │    │                  │    │                 │
│ • Data cleaning │    │ • Visual reports │    │ • CSV/Excel     │
│ • Error handle  │    │ • Analytics      │    │ • LinkedIn URLs │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Components

### 1. Web Scraper (`scraper.py`)
- Real-time scraping of company websites
- Revenue and employee count extraction
- Multiple data source integration (LinkedIn, Crunchbase)

### 2. Lead Processor (`lead_processor.py`)
- Event and association research
- Company prioritization by revenue/size
- Decision maker identification
- Qualification rationale generation

### 3. DeepSeek Integration (`deepseek_client.py`)
- Company data enrichment
- Personalized outreach message generation
- Market intelligence and strategic insights

### 4. Dashboard (`dashboard.py`)
- Lead visualization and analytics
- Export functionality (CSV/Excel)
- Performance metrics and reporting

## Data Flow

1. **Event Research** - Identify relevant industry events and associations
2. **Company Extraction** - Extract companies from event data
3. **Data Scraping** - Gather company information from multiple sources
4. **AI Enrichment** - Use DeepSeek to analyze and enhance data
5. **Persona ID** - Identify key decision makers and contact information
6. **Outreach Gen** - Create personalized messages for each lead
7. **Validation** - Clean and validate all data
8. **Dashboard** - Present results in visual format

## Sample Output

### Generated Lead Example

```json
{
  "company_name": "Avery Dennison Graphics Solutions",
  "website": "https://graphics.averydennison.com",
  "estimated_revenue": 8500000000,
  "employees": "10,000+",
  "industry": "Graphics & Signage",
  "qualification_rationale": "Avery Dennison is a qualified lead for DuPont Tedlar because it's a large enterprise with $8.5B+ in annual revenue, it specializes in graphics & signage solutions where Tedlar's protective films provide significant value...",
  "primary_contact": {
    "name": "Sarah Dennison",
    "title": "VP of Product Development",
    "email": "sarah.dennison@averydennison.com",
    "linkedin_url": "https://www.linkedin.com/in/sarah-dennison-avery/"
  },
  "outreach_message": "Hi Sarah, I noticed Avery Dennison's leadership in graphics solutions. As VP of Product Development, I thought you might be interested in how DuPont Tedlar's protective films could enhance your product durability..."
}
```

## Error Handling

- **API Failures** - Graceful fallback to cached/mock data
- **Scraping Issues** - Retry logic with exponential backoff
- **Data Validation** - Comprehensive validation with detailed error messages
- **Rate Limiting** - Built-in delays to respect API limits

## Performance & Scalability

- **Concurrent Processing** - Async/await for parallel data collection
- **Rate Limiting** - Built-in delays and request throttling
- **Caching** - Response caching to reduce API calls
- **Batch Processing** - Efficient batch operations for large datasets

## Cost Management

- **LLM Budget** - Up to $200/month for DeepSeek API calls
- **Efficient Prompting** - Optimized prompts to minimize token usage
- **Caching Strategy** - Reduce redundant API calls
- **Batch Optimization** - Process multiple companies per API call

## Future Enhancements

### Phase 1 (MVP)
- ✅ Basic lead generation and enrichment
- ✅ Personalized outreach messages
- ✅ Dashboard and reporting

### Phase 2 (Enhanced)
- 🔄 LinkedIn Sales Navigator integration
- 🔄 Clay API data enrichment
- 🔄 Advanced persona identification
- 🔄 Email verification and validation

### Phase 3 (Enterprise)
- 🔄 CRM integration (Salesforce, HubSpot)
- 🔄 Automated outreach sending
- 🔄 Advanced analytics and reporting
- 🔄 Multi-touch campaign management

## Support

For issues or questions:
1. Check the logs in the application
2. Review the error handling documentation
3. Test with the provided test script
4. Check API rate limits and quotas

## License

This project is developed for DuPont Tedlar's Graphics & Signage team.
