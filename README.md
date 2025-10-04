# DuPont Tedlar AI Lead Generation Agent

## Overview
This documentation outlines an AI agent created for DuPont Tedlar’s Graphics & Signage division to automate lead generation. The agent leverages AI to identify potential customers at industry events, enrich company profiles with validated data, and generate personalized outreach messages. The primary goal is to reduce the sales team’s manual workload while maintaining data accuracy, scalability, and professional communication quality.

---

## AI Agent Workflow and Architecture
The AI agent follows a multi-stage automated workflow designed for accuracy and performance:  
- First, DeepSeek AI identifies relevant trade shows in the target industry.  
- The AI then filters industry-leading companies, prioritizing high-value targets and removing invalid or incomplete records.  
- A dynamic website discovery algorithm locates each company’s websites. The system extracts key data such as descriptions, revenue, and employee counts from the websites.  
- The AI identifies relevant executives (VP and Director level) and explains their strategic significance. It is designed to integrate seamlessly with LinkedIn Sales Navigator for live contact data.  
- Finally, the AI drafts tailored outreach notes for each identified persona.  

---

## Technical Implementation: System Components
The AI agent is built using a scalable, modular architecture optimized for asynchronous performance and API extensibility:  

- **Frontend:** Streamlit dashboard for user interaction and visualization.  
- **AI Engine:** DeepSeek API via OpenRouter using GPT-4-class reasoning (leveraging the free open-source model).  
  - The free model is sufficient for this use case as it provides strong reasoning and data validation capabilities, handles controlled lead volume within free tier limits, and delivers reliable, professional outputs without incurring extra costs.  
- **Data Collection:** Asynchronous web scraping via aiohttp and BeautifulSoup for concurrent lead processing.  
- **Processing Layer:** Python with async/await for concurrency and optimized performance.  
- **Data Output:** Can be exported to CSV/Excel formats.  
- **Error Handling:** Designed the system to fail gracefully, with multiple layers of fault recovery and thorough API validation to ensure reliability.  
- **Scalability:** Supports enterprise deployment through rate limiting, modular architecture, and ready integration points for LinkedIn and Clay.  

---

## Data Structure
The AI agent stores and manages structured lead information for each company, ensuring all relevant details are captured for both analysis and outreach.  

Key fields for each company include:  
- Company name  
- Official website  
- Annual revenue  
- Employee count  
- Participation in industry events  
- Identified decision makers with roles and relevance rationales  
- Personalized outreach drafts  

This structured approach enables consistent data handling across the pipeline and export to CSV or Excel with clear column headers corresponding to each field.  

---

## Data Processing Pipeline
The pipeline executes in four main stages to maintain accuracy and structure:  
1. AI identifies 5–7 key industry events relevant to the Graphics & Signage sector  
2. Generates and prioritizes firms, filtering by validated revenue  
3. Extracts descriptive and strategic company data using DeepSeek  
4. Surfaces decision makers with role-based rationales and drafts tailored outreach messages  

---

## Dashboard and User Experience
The Streamlit dashboard provides an intuitive interface for both visualization and operational control.  

- Users can define the market focus by entering a keyword in the **Target Industry** search, which the AI then uses to identify relevant events and companies.  
- A **Number of Leads** slider allows users to control how many leads (up to 20) are generated at once, balancing processing speed with data depth.  
- Each generated company includes detailed information such as industry fit, revenue, strategic relevance, market activity, decision makers, and personalized outreach drafts.  

The dashboard layout positions the list of companies on the left, with detailed information displayed in the center, and the outreach drafts can be directly edited or copy-pasted.  

Finally, users can export the generated data with a single click to CSV or Excel files for seamless integration with other tools.  

---

## Testing and Validation
To ensure data accuracy and reliability, the AI agent employs multiple validation layers.  

- All company revenue and employee data are checked for consistency and completeness, with entries failing validation flagged for review.  
- The system also monitors for rare AI hallucinations or incomplete outputs in decision maker identification and outreach drafts, applying fallback logic or prompting manual review when anomalies are detected.  

---

## Current Limitations
- The system currently lacks retry logic and quickly reaches OpenRouter’s free tier request caps (rate limiting), which restricts continuous use.  
- Since the agent is using the free tier of DeepSeek’s model, it is limited to processing around 50–70 leads per day and may occasionally produce incomplete data or hallucinations.  
- Because requests aren’t cached, repeated searches for the same industry or company in order to look for missing company info consumes additional API calls unnecessarily.  
- Currently, the agent processes leads one by one, taking up to 2 minutes per lead. This can be optimized by introducing a task queue that will allow the system to process dozens of leads simultaneously (i.e. parallelizing the workflow).  

---

## Future Additions / Roadmap
- Extend modular architecture to handle more leads or industries with minimal changes  
- Upgrade to a paid DeepSeek/OpenRouter tier for higher throughput  
- Add retry and caching mechanisms to reduce wasted API calls  
- Expand decision maker roles and LinkedIn/Clay integration  
- Enhance dashboard with charts/graphs for visual analytics  
- Use of asynchronous processing with task queues  
