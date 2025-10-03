"""
Dashboard generator for lead visualization and reporting
"""

import json
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd

class DashboardGenerator:
    """Generates dashboard data for lead visualization"""

    def create_dashboard(self, leads: List[Dict]) -> Dict:
        """Create comprehensive dashboard data"""
        dashboard_data = {
            'summary': self._generate_summary(leads),
            'top_leads': self._get_top_leads(leads),
            'leads_by_industry': self._group_by_industry(leads),
            'leads_by_revenue': self._group_by_revenue(leads),
            'recent_activity': self._generate_activity_feed(leads),
            'export_data': self._prepare_export_data(leads)
        }

        return dashboard_data

    def _generate_summary(self, leads: List[Dict]) -> Dict:
        """Generate summary statistics"""
        total_leads = len(leads)
        total_revenue = sum(lead.get('estimated_revenue', 0) for lead in leads)
        avg_revenue = total_revenue / total_leads if total_leads > 0 else 0

        # Count by company size
        large_companies = sum(1 for lead in leads if lead.get('estimated_revenue', 0) >= 1000000000)
        medium_companies = sum(1 for lead in leads if 100000000 <= lead.get('estimated_revenue', 0) < 1000000000)

        return {
            'total_leads': total_leads,
            'total_estimated_revenue': total_revenue,
            'average_revenue': avg_revenue,
            'large_companies': large_companies,
            'medium_companies': medium_companies,
            'generated_at': datetime.utcnow().isoformat()
        }

    def _get_top_leads(self, leads: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top leads by revenue"""
        # Sort by revenue descending
        sorted_leads = sorted(leads, key=lambda x: x.get('estimated_revenue', 0), reverse=True)

        top_leads = []
        for lead in sorted_leads[:limit]:
            top_lead = {
                'company_name': lead.get('company_name', 'Unknown'),
                'website': lead.get('website', ''),
                'estimated_revenue': lead.get('estimated_revenue', 0),
                'employees': lead.get('employees', 'Unknown'),
                'industry': lead.get('industry', 'Unknown'),
                'qualification_rationale': lead.get('qualification_rationale', '')[:200] + '...',
                'primary_contact': lead.get('primary_contact', {}),
                'outreach_message': lead.get('outreach_message', '')[:150] + '...'
            }
            top_leads.append(top_lead)

        return top_leads

    def _group_by_industry(self, leads: List[Dict]) -> Dict:
        """Group leads by industry"""
        industry_groups = {}

        for lead in leads:
            industry = lead.get('industry', 'Other')
            if industry not in industry_groups:
                industry_groups[industry] = []
            industry_groups[industry].append(lead)

        # Convert to display format
        result = {}
        for industry, industry_leads in industry_groups.items():
            result[industry] = {
                'count': len(industry_leads),
                'companies': [lead.get('company_name', 'Unknown') for lead in industry_leads[:5]],  # Top 5
                'total_revenue': sum(lead.get('estimated_revenue', 0) for lead in industry_leads)
            }

        return result

    def _group_by_revenue(self, leads: List[Dict]) -> Dict:
        """Group leads by revenue ranges"""
        ranges = {
            '$10B+': (10000000000, float('inf')),
            '$1B-$10B': (1000000000, 10000000000),
            '$100M-$1B': (100000000, 1000000000),
            '$10M-$100M': (10000000, 100000000),
            'Under $10M': (0, 10000000)
        }

        revenue_groups = {range_name: [] for range_name in ranges.keys()}

        for lead in leads:
            revenue = lead.get('estimated_revenue', 0)
            for range_name, (min_val, max_val) in ranges.items():
                if min_val <= revenue < max_val:
                    revenue_groups[range_name].append(lead)
                    break

        # Convert to display format
        result = {}
        for range_name, range_leads in revenue_groups.items():
            if range_leads:  # Only include non-empty ranges
                result[range_name] = {
                    'count': len(range_leads),
                    'companies': [lead.get('company_name', 'Unknown') for lead in range_leads[:5]],
                    'total_revenue': sum(lead.get('estimated_revenue', 0) for lead in range_leads)
                }

        return result

    def _generate_activity_feed(self, leads: List[Dict]) -> List[Dict]:
        """Generate recent activity feed"""
        activities = []

        for lead in leads[:20]:  # Last 20 leads for activity feed
            activity = {
                'type': 'lead_generated',
                'company': lead.get('company_name', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'revenue': lead.get('estimated_revenue', 0),
                'message': f"Generated lead for {lead.get('company_name', 'Unknown')} with estimated ${lead.get('estimated_revenue', 0)/1000000:.0f}M revenue",
                'contact': lead.get('primary_contact', {}).get('name', 'Unknown')
            }
            activities.append(activity)

        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        return activities

    def _prepare_export_data(self, leads: List[Dict]) -> Dict:
        """Prepare data for export to CSV/Excel"""
        export_data = []

        for lead in leads:
            export_row = {
                'Company Name': lead.get('company_name', ''),
                'Website': lead.get('website', ''),
                'Estimated Revenue': lead.get('estimated_revenue', 0),
                'Employees': lead.get('employees', ''),
                'Industry': lead.get('industry', ''),
                'Qualification Rationale': lead.get('qualification_rationale', ''),
                'Primary Contact': lead.get('primary_contact', {}).get('name', ''),
                'Contact Title': lead.get('primary_contact', {}).get('title', ''),
                'Contact Email': lead.get('primary_contact', {}).get('email', ''),
                'LinkedIn URL': lead.get('primary_contact', {}).get('linkedin_url', ''),
                'Outreach Message': lead.get('outreach_message', ''),
                'Source Event': ', '.join(lead.get('events_attending', [])),
                'Generated At': datetime.utcnow().isoformat()
            }
            export_data.append(export_row)

        return {
            'csv_data': export_data,
            'column_headers': list(export_data[0].keys()) if export_data else []
        }

    def export_to_csv(self, leads: List[Dict], filename: str = 'leads_export.csv'):
        """Export leads to CSV file"""
        export_data = self._prepare_export_data(leads)

        if not export_data['csv_data']:
            return False

        df = pd.DataFrame(export_data['csv_data'])
        df.to_csv(filename, index=False)

        return True

    def export_to_excel(self, leads: List[Dict], filename: str = 'leads_export.xlsx'):
        """Export leads to Excel file"""
        export_data = self._prepare_export_data(leads)

        if not export_data['csv_data']:
            return False

        df = pd.DataFrame(export_data['csv_data'])

        # Create Excel file with multiple sheets
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main leads sheet
            df.to_excel(writer, sheet_name='Leads', index=False)

            # Summary sheet
            summary_df = pd.DataFrame([self._generate_summary(leads)])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Industry breakdown
            industry_data = self._group_by_industry(leads)
            industry_df = pd.DataFrame([
                {'Industry': industry, **data}
                for industry, data in industry_data.items()
            ])
            if not industry_df.empty:
                industry_df.to_excel(writer, sheet_name='By Industry', index=False)

        return True
