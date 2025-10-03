"""
Error handling and data validation utilities
"""

import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, ValidationError, validator
import re

logger = logging.getLogger(__name__)

class LeadValidationError(Exception):
    """Custom exception for lead validation errors"""
    pass

class CompanyDataValidator:
    """Validates company data"""

    @staticmethod
    def validate_company_data(company: Dict) -> Dict:
        """Validate and clean company data"""
        try:
            # Required fields
            if not company.get('company_name'):
                raise LeadValidationError("Company name is required")

            if not company.get('website'):
                logger.warning(f"No website found for {company.get('company_name', 'Unknown')}")
            else:
                # Validate website format
                if not CompanyDataValidator._is_valid_url(company['website']):
                    logger.warning(f"Invalid website URL for {company['company_name']}: {company['website']}")

            # Validate revenue if present
            if 'estimated_revenue' in company:
                revenue = company['estimated_revenue']
                if not isinstance(revenue, (int, float)) or revenue < 0:
                    logger.warning(f"Invalid revenue value for {company['company_name']}: {revenue}")
                    company['estimated_revenue'] = 0

            # Validate employee count if present
            if 'employees' in company:
                employees = company['employees']
                if employees and not isinstance(employees, (int, str)):
                    logger.warning(f"Invalid employee count for {company['company_name']}: {employees}")
                    company['employees'] = 'Unknown'

            # Clean company name
            company['company_name'] = CompanyDataValidator._clean_company_name(company['company_name'])

            return company

        except Exception as e:
            logger.error(f"Error validating company data: {str(e)}")
            raise LeadValidationError(f"Company validation failed: {str(e)}")

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        try:
            regex = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            return bool(regex.match(url))
        except:
            return False

    @staticmethod
    def _clean_company_name(name: str) -> str:
        """Clean and standardize company name"""
        if not name:
            return "Unknown"

        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())

        # Remove common suffixes that don't add value
        suffixes_to_remove = [
            r'\s+Ltd\.?$',
            r'\s+LLC\.?$',
            r'\s+Inc\.?$',
            r'\s+Corp\.?$',
            r'\s+Corporation\.?$',
            r'\s+Limited\.?$',
            r'\s+Co\.?$',
            r'\s+Company\.?$'
        ]

        for suffix in suffixes_to_remove:
            name = re.sub(suffix, '', name, flags=re.IGNORECASE)

        return name.strip()

class ContactDataValidator:
    """Validates contact data"""

    @staticmethod
    def validate_contact_data(contact: Dict) -> Dict:
        """Validate and clean contact data"""
        try:
            # Required fields
            if not contact.get('name'):
                raise LeadValidationError("Contact name is required")

            if not contact.get('title'):
                logger.warning(f"No title found for contact {contact.get('name', 'Unknown')}")

            # Validate email if present
            if 'email' in contact and contact['email']:
                if not ContactDataValidator._is_valid_email(contact['email']):
                    logger.warning(f"Invalid email for {contact.get('name', 'Unknown')}: {contact['email']}")
                    contact['email'] = ''

            # Validate LinkedIn URL if present
            if 'linkedin_url' in contact and contact['linkedin_url']:
                if not ContactDataValidator._is_valid_linkedin_url(contact['linkedin_url']):
                    logger.warning(f"Invalid LinkedIn URL for {contact.get('name', 'Unknown')}: {contact['linkedin_url']}")
                    contact['linkedin_url'] = ''

            # Clean name
            contact['name'] = ContactDataValidator._clean_contact_name(contact['name'])

            return contact

        except Exception as e:
            logger.error(f"Error validating contact data: {str(e)}")
            raise LeadValidationError(f"Contact validation failed: {str(e)}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Check if email is valid"""
        try:
            regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            return bool(regex.match(email))
        except:
            return False

    @staticmethod
    def _is_valid_linkedin_url(url: str) -> bool:
        """Check if LinkedIn URL is valid"""
        try:
            if not url.startswith('https://www.linkedin.com/'):
                return False
            # Basic check for LinkedIn profile URL pattern
            return '/in/' in url or '/company/' in url
        except:
            return False

    @staticmethod
    def _clean_contact_name(name: str) -> str:
        """Clean and standardize contact name"""
        if not name:
            return "Unknown"

        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())

        # Capitalize properly
        parts = name.split()
        capitalized_parts = []
        for part in parts:
            if len(part) > 0:
                capitalized_parts.append(part.capitalize())

        return ' '.join(capitalized_parts)

class ErrorHandler:
    """Central error handling and recovery"""

    @staticmethod
    def handle_api_error(error: Exception, context: str) -> Dict:
        """Handle API-related errors"""
        logger.error(f"API error in {context}: {str(error)}")

        return {
            'success': False,
            'error': str(error),
            'context': context,
            'error_type': 'api_error',
            'timestamp': None  # Would import datetime here
        }

    @staticmethod
    def handle_scraping_error(error: Exception, url: str) -> Dict:
        """Handle web scraping errors"""
        logger.error(f"Scraping error for {url}: {str(error)}")

        return {
            'success': False,
            'error': str(error),
            'url': url,
            'error_type': 'scraping_error'
        }

    @staticmethod
    def handle_validation_error(error: ValidationError) -> Dict:
        """Handle Pydantic validation errors"""
        logger.error(f"Validation error: {error}")

        return {
            'success': False,
            'error': str(error),
            'error_type': 'validation_error',
            'field_errors': error.errors() if hasattr(error, 'errors') else []
        }

    @staticmethod
    def create_fallback_response(context: str) -> Dict:
        """Create fallback response when errors occur"""
        return {
            'success': False,
            'error': 'Service temporarily unavailable',
            'context': context,
            'fallback': True,
            'data': []
        }

class DataSanitizer:
    """Data sanitization utilities"""

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove HTML tags from text"""
        if not text:
            return ""

        # Basic HTML tag removal
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """Sanitize and truncate text"""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + "..."

        return text

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number format"""
        if not phone:
            return ""

        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)

        # Format as US phone number
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith('1'):
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

        return phone  # Return original if can't normalize

def validate_leads_batch(leads: List[Dict]) -> List[Dict]:
    """Validate a batch of leads"""
    validated_leads = []

    for lead in leads:
        try:
            # Validate company data
            validated_company = CompanyDataValidator.validate_company_data(lead.copy())

            # Validate contacts if present
            if 'contacts' in validated_company:
                validated_contacts = []
                for contact in validated_company['contacts']:
                    try:
                        validated_contact = ContactDataValidator.validate_contact_data(contact.copy())
                        validated_contacts.append(validated_contact)
                    except LeadValidationError as e:
                        logger.warning(f"Skipping invalid contact: {str(e)}")
                        continue
                validated_company['contacts'] = validated_contacts

            validated_leads.append(validated_company)

        except LeadValidationError as e:
            logger.warning(f"Skipping invalid lead: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error validating lead: {str(e)}")
            continue

    return validated_leads
