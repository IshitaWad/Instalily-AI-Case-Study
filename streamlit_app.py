"""
Streamlit Web App for Lead Generation AI Agent
Beautiful dashboard interface for generating and viewing leads
"""

import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our components
from scraper import WebScraper
from deepseek_client import DeepSeekClient
from real_data_processor import RealDataLeadProcessor
from dashboard import DashboardGenerator
from validation import validate_leads_batch

# Page configuration
st.set_page_config(
    page_title="Lead Generation AI Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .lead-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'dashboard_data' not in st.session_state:
    st.session_state.dashboard_data = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Header
st.markdown('<div class="main-header">🎯 Lead Generation AI Agent</div>', unsafe_allow_html=True)
st.markdown("### Automated Lead Generation & Personalized Outreach for DuPont Tedlar")
st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key status
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key and api_key != 'your_deepseek_api_key_here':
        st.success("✅ API Key Configured")
    else:
        st.error("❌ API Key Not Found")
        st.info("Add DEEPSEEK_API_KEY to .env file")
    
    st.markdown("---")
    
    # Generation settings
    st.subheader("🎯 Generation Settings")
    
    industry = st.text_input(
        "Target Industry",
        value="Graphics & Signage",
        help="Industry to research for leads"
    )
    
    max_leads = st.slider(
        "Number of Leads",
        min_value=1,
        max_value=20,
        value=3,
        help="More leads = longer processing time"
    )
    
    use_real_data = st.checkbox(
        "Use 100% Real Data",
        value=False,
        help="Uses AI and web scraping (slower, uses API calls)"
    )
    
    st.markdown("---")
    
    # Generate button
    generate_button = st.button(
        "🚀 Generate Leads",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Export options
    if st.session_state.leads:
        st.subheader("📥 Export Options")
        
        if st.button("Download CSV", use_container_width=True):
            dashboard_gen = DashboardGenerator()
            dashboard_gen.export_to_csv(st.session_state.leads, 'leads_export.csv')
            st.success("✅ Exported to leads_export.csv")
        
        if st.button("Download Excel", use_container_width=True):
            dashboard_gen = DashboardGenerator()
            dashboard_gen.export_to_excel(st.session_state.leads, 'leads_export.xlsx')
            st.success("✅ Exported to leads_export.xlsx")

# Main content area
if generate_button:
    st.session_state.processing = True
    
    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    async def generate_leads_async():
        try:
            # Initialize components
            status_text.text("🔧 Initializing components...")
            progress_bar.progress(10)
            
            scraper = WebScraper()
            deepseek_client = DeepSeekClient(api_key)
            
            if use_real_data:
                # Use real data processor
                status_text.text("🔍 Researching industry events with AI...")
                progress_bar.progress(20)
                
                processor = RealDataLeadProcessor(scraper, deepseek_client)
                
                status_text.text("🏢 Identifying companies with AI...")
                progress_bar.progress(40)
                
                status_text.text("🌐 Scraping real company data...")
                progress_bar.progress(60)
                
                status_text.text("🧠 Enriching with AI analysis...")
                progress_bar.progress(80)
                
                leads = await processor.generate_real_leads(industry, max_results=max_leads)
            else:
                # Use demo mode with clean mock data
                from lead_processor import LeadProcessor
                
                status_text.text("📊 Processing sample companies...")
                progress_bar.progress(30)
                
                # Sample companies with proper data
                sample_companies = [
                    {
                        'name': 'Avery Dennison Graphics Solutions',
                        'company_name': 'Avery Dennison Graphics Solutions',
                        'website': 'https://graphics.averydennison.com',
                        'estimated_revenue': 8500000000,
                        'employees': 10000,
                        'industry': 'Graphics & Signage',
                        'description': 'Leading manufacturer of graphics and signage materials',
                        'events_attending': ['ISA Sign Expo', 'PRINTING United', 'SGIA Expo']
                    },
                    {
                        'name': '3M Commercial Graphics',
                        'company_name': '3M Commercial Graphics',
                        'website': 'https://www.3m.com/graphics',
                        'estimated_revenue': 35000000000,
                        'employees': 95000,
                        'industry': 'Graphics & Signage',
                        'description': 'Global leader in commercial graphics solutions',
                        'events_attending': ['ISA Sign Expo', 'PRINTING United', 'Graphics & Signage Expo']
                    },
                    {
                        'name': 'Arlon Graphics',
                        'company_name': 'Arlon Graphics',
                        'website': 'https://www.arlon.com',
                        'estimated_revenue': 500000000,
                        'employees': 1200,
                        'industry': 'Graphics & Signage',
                        'description': 'Manufacturer of high-performance graphic films',
                        'events_attending': ['SGIA Expo', 'FESPA Global', 'ISA Sign Expo']
                    },
                    {
                        'name': 'FDC Graphic Films',
                        'company_name': 'FDC Graphic Films',
                        'website': 'https://www.fdcfilms.com',
                        'estimated_revenue': 300000000,
                        'employees': 800,
                        'industry': 'Graphics & Signage',
                        'description': 'Specialty films for graphics applications',
                        'events_attending': ['ISA Sign Expo', 'PRINTING United']
                    },
                    {
                        'name': 'Mactac Graphics',
                        'company_name': 'Mactac Graphics',
                        'website': 'https://www.mactac.com/graphics',
                        'estimated_revenue': 600000000,
                        'employees': 1500,
                        'industry': 'Graphics & Signage',
                        'description': 'Pressure-sensitive adhesive solutions',
                        'events_attending': ['PRINTING United', 'Labelexpo', 'SGIA Expo']
                    }
                ][:max_leads]
                
                status_text.text("🔍 Generating qualification rationale...")
                progress_bar.progress(50)
                
                # Add qualification rationale
                processor = LeadProcessor(scraper, deepseek_client)
                for company in sample_companies:
                    company['qualification_rationale'] = processor._generate_qualification_rationale(company)
                
                status_text.text("👥 Identifying decision makers...")
                progress_bar.progress(70)
                with_contacts = await processor.identify_decision_makers(sample_companies)
                
                status_text.text("💬 Generating personalized outreach...")
                progress_bar.progress(90)
                leads = await processor.generate_outreach_messages(with_contacts)
            
            # Validate leads
            status_text.text("✅ Validating leads...")
            progress_bar.progress(95)
            validated_leads = validate_leads_batch(leads)
            
            # Generate dashboard data
            dashboard_gen = DashboardGenerator()
            dashboard_data = dashboard_gen.create_dashboard(validated_leads)
            
            # Store in session state
            st.session_state.leads = validated_leads
            st.session_state.dashboard_data = dashboard_data
            
            progress_bar.progress(100)
            status_text.text("✅ Lead generation complete!")
            
            # Cleanup
            await scraper.close()
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return False
    
    # Run async function
    success = asyncio.run(generate_leads_async())
    
    if success:
        st.balloons()
        st.rerun()

# Display results
if st.session_state.leads and st.session_state.dashboard_data:
    # Summary metrics
    st.header("📊 Summary Dashboard")
    
    summary = st.session_state.dashboard_data['summary']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Leads",
            summary['total_leads'],
            delta=None
        )
    
    with col2:
        if summary.get('total_estimated_revenue', 0) > 0:
            revenue_b = summary['total_estimated_revenue'] / 1000000000
            st.metric(
                "Total Revenue",
                f"${revenue_b:.1f}B",
                delta=None
            )
        else:
            st.metric("Total Revenue", "N/A")
    
    with col3:
        if summary.get('average_revenue', 0) > 0:
            avg_m = summary['average_revenue'] / 1000000
            st.metric(
                "Avg Revenue",
                f"${avg_m:.0f}M",
                delta=None
            )
        else:
            st.metric("Avg Revenue", "N/A")
    
    with col4:
        st.metric(
            "Large Companies",
            summary.get('large_companies', 0),
            delta=None
        )
    
    st.markdown("---")
    
    # Initialize selected lead index
    if 'selected_lead_index' not in st.session_state:
        st.session_state.selected_lead_index = 0
    
    # Create two columns: sidebar list and main detail view
    col_list, col_detail = st.columns([1, 3])
    
    # Left column: Company list
    with col_list:
        st.markdown("### 📋 Companies")
        st.markdown("Click to view details →")
        
        for i, lead in enumerate(st.session_state.leads):
            # Create a button for each company
            company_name = lead.get('company_name', 'Unknown')
            revenue = lead.get('estimated_revenue', 0)
            
            if revenue >= 1000000000:
                revenue_str = f"${revenue/1000000000:.1f}B"
            elif revenue > 0:
                revenue_str = f"${revenue/1000000:.0f}M"
            else:
                revenue_str = "N/A"
            
            # Highlight selected company
            if i == st.session_state.selected_lead_index:
                button_type = "primary"
            else:
                button_type = "secondary"
            
            if st.button(
                f"{i+1}. {company_name}\n{revenue_str}",
                key=f"company_btn_{i}",
                type=button_type,
                use_container_width=True
            ):
                st.session_state.selected_lead_index = i
                st.rerun()
            
            st.markdown("---")
    
    # Right column: Detailed view of selected company
    with col_detail:
        if st.session_state.leads:
            lead = st.session_state.leads[st.session_state.selected_lead_index]
            
            # Company header
            st.markdown(f"# {lead.get('company_name', 'Unknown')}")
            
            # Revenue metric
            revenue = lead.get('estimated_revenue', 0)
            col1, col2, col3 = st.columns(3)
            with col1:
                if revenue >= 1000000000:
                    st.metric("Revenue", f"${revenue/1000000000:.1f}B")
                elif revenue > 0:
                    st.metric("Revenue", f"${revenue/1000000:.0f}M")
                else:
                    st.metric("Revenue", "N/A")
            with col2:
                st.metric("Employees", f"{lead.get('employees', 'Unknown'):,}" if isinstance(lead.get('employees'), int) else lead.get('employees', 'Unknown'))
            with col3:
                st.metric("Industry", lead.get('industry', 'N/A'))
            
            st.markdown("---")
            
            # Website
            st.markdown("### 🌐 Website")
            website = lead.get('website', 'N/A')
            if website != 'N/A' and website.startswith('http'):
                st.markdown(f"[{website}]({website})")
            else:
                st.write(website)
            
            # Events attending
            if lead.get('events_attending'):
                st.markdown("### 🎪 Events Attending")
                events_list = lead['events_attending']
                if isinstance(events_list, list):
                    for event in events_list:
                        st.write(f"• {event}")
                else:
                    st.write(f"• {events_list}")
            
            # Qualification rationale
            st.markdown("### 💡 Why This Lead Matters")
            st.info(lead.get('qualification_rationale', 'N/A'))
            
            # Decision makers
            if lead.get('decision_makers'):
                st.markdown("### 👥 Decision Makers")
                for dm in lead['decision_makers'][:3]:
                    with st.expander(f"**{dm.get('title', 'N/A')}**"):
                        st.write(dm.get('relevance', 'Key decision maker'))
            
            # Primary contact
            if lead.get('primary_contact'):
                contact = lead['primary_contact']
                st.markdown("### 📧 Primary Contact")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {contact.get('name', 'N/A')}")
                    st.write(f"**Title:** {contact.get('title', 'N/A')}")
                with col2:
                    st.write(f"**Email:** {contact.get('email', 'N/A')}")
                    if contact.get('linkedin_url') and contact.get('linkedin_url') != 'N/A':
                        st.markdown(f"[🔗 LinkedIn Profile]({contact['linkedin_url']})")
            
            # Outreach message
            if lead.get('outreach_message'):
                st.markdown("### 💬 Personalized Outreach Message")
                st.text_area(
                    "Copy this message for your outreach:",
                    lead['outreach_message'],
                    height=250,
                    key=f"outreach_detail_{st.session_state.selected_lead_index}",
                    label_visibility="collapsed"
                )
                
                # Copy button hint
                st.caption("💡 Tip: Click in the text area and press Ctrl+A then Ctrl+C to copy")
    
    st.markdown("---")
    
    # Tabs for analytics and export
    tab1, tab2 = st.tabs(["📊 Analytics", "📁 Export Data"])
    
    with tab1:
        st.header("Analytics")
        
        # Revenue distribution
        if st.session_state.dashboard_data.get('leads_by_revenue'):
            st.subheader("📊 Revenue Distribution")
            revenue_data = st.session_state.dashboard_data['leads_by_revenue']
            
            df_revenue = pd.DataFrame([
                {'Range': range_name, 'Count': data['count'], 'Total Revenue': data['total_revenue']}
                for range_name, data in revenue_data.items()
            ])
            
            if not df_revenue.empty:
                st.bar_chart(df_revenue.set_index('Range')['Count'])
        
        # Industry breakdown
        if st.session_state.dashboard_data.get('leads_by_industry'):
            st.subheader("🏢 Industry Breakdown")
            industry_data = st.session_state.dashboard_data['leads_by_industry']
            
            df_industry = pd.DataFrame([
                {'Industry': industry, 'Count': data['count']}
                for industry, data in industry_data.items()
            ])
            
            if not df_industry.empty:
                st.bar_chart(df_industry.set_index('Industry')['Count'])
    
    with tab2:
        st.header("Export Data")
        
        # Prepare export data
        export_data = st.session_state.dashboard_data.get('export_data', {}).get('csv_data', [])
        
        if export_data:
            df = pd.DataFrame(export_data)
            
            st.subheader("📋 Preview")
            st.dataframe(df, use_container_width=True)
            
            st.subheader("📥 Download")
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name=f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # For Excel, we'll use the dashboard generator
                if st.button("📊 Generate Excel", use_container_width=True):
                    dashboard_gen = DashboardGenerator()
                    excel_file = f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    dashboard_gen.export_to_excel(st.session_state.leads, excel_file)
                    st.success(f"✅ Excel file generated: {excel_file}")

else:
    # Welcome screen
    st.info("👈 Configure settings in the sidebar and click **Generate Leads** to start!")
    
    st.markdown("### 🎯 Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 AI-Powered Research**
        - Event identification
        - Company discovery
        - Market intelligence
        """)
    
    with col2:
        st.markdown("""
        **👥 Decision Maker ID**
        - VP/Director targeting
        - Role-based personas
        - Contact information
        """)
    
    with col3:
        st.markdown("""
        **💬 Personalized Outreach**
        - AI-generated messages
        - Company-specific
        - Professional tone
        """)
    
    st.markdown("---")
    
    st.markdown("### 📊 Sample Output")
    st.image("https://via.placeholder.com/800x400/1f77b4/ffffff?text=Lead+Generation+Dashboard", use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Built with ❤️ for DuPont Tedlar | Powered by DeepSeek AI</div>",
    unsafe_allow_html=True
)
