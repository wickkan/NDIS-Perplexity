"""
Response Formatter for NDIS Decoder
Standardizes output formats for different query types with confidence indicators
"""
import json
import re
from datetime import datetime

class NDISResponseFormatter:
    def __init__(self):
        """Initialize the NDIS response formatter"""
        # Define standard templates for different response types
        self.templates = {
            "code_lookup": {
                "support_codes": [],
                "explanation": "",
                "price_caps": {},
                "rules": [],
                "confidence_score": 0.0,
                "citations": [],
                "summary": ""
            },
            "policy_guidance": {
                "topic": "",
                "guidance": "",
                "key_points": [],
                "citations": [],
                "confidence_score": 0.0,
                "related_policies": [],
                "summary": ""
            },
            "service_recommendation": {
                "needs_addressed": [],
                "recommended_services": [],
                "support_categories": [],
                "rationale": "",
                "confidence_score": 0.0,
                "citations": [],
                "summary": ""
            },
            "ndis_updates": {
                "update_period": "",
                "updates": [],
                "impact_assessment": "",
                "confidence_score": 0.0,
                "citations": [],
                "summary": ""
            },
            "budget_planning": {
                "total_amount": 0.0,
                "allocations": [],
                "rationale": "",
                "confidence_score": 0.0,
                "notes": "",
                "summary": ""
            }
        }
        
    def format_response(self, response_data, response_type, original_data=None):
        """
        Format raw response data into standardized template
        
        Args:
            response_data (dict): Raw response data from the API
            response_type (str): Type of response to format
            original_data (dict, optional): Original user request data
            
        Returns:
            dict: Formatted response
        """
        if response_type not in self.templates:
            return response_data  # Return as-is if no template exists
            
        # Create a copy of the template
        formatted = self.templates[response_type].copy()
        
        # Apply specific formatting based on response type
        if response_type == "code_lookup":
            return self._format_code_lookup(formatted, response_data)
        elif response_type == "policy_guidance":
            return self._format_policy_guidance(formatted, response_data)
        elif response_type == "service_recommendation":
            return self._format_service_recommendation(formatted, response_data, original_data)
        elif response_type == "ndis_updates":
            return self._format_ndis_updates(formatted, response_data)
        elif response_type == "budget_planning":
            return self._format_budget_planning(formatted, response_data, original_data)
            
        # Fallback - return original with added summary
        if "summary" not in response_data and response_data.get("explanation"):
            response_data["summary"] = self._generate_summary(response_data["explanation"])
        return response_data
        
    def _format_code_lookup(self, template, data):
        """Format code lookup response"""
        # Transfer existing fields
        if "support_codes" in data:
            template["support_codes"] = data["support_codes"]
        if "explanation" in data:
            template["explanation"] = data["explanation"]
        if "price_caps" in data:
            template["price_caps"] = data["price_caps"]
        if "rules" in data:
            template["rules"] = data["rules"]
            
        # Extract citations
        if "citations" in data:
            template["citations"] = data["citations"]
        elif "explanation" in data:
            # Extract URLs from explanation as fallback
            template["citations"] = self._extract_citations(data["explanation"])
            
        # Calculate confidence score
        template["confidence_score"] = self._calculate_confidence_score(data)
        
        # Generate concise summary
        if "explanation" in data:
            template["summary"] = self._generate_summary(data["explanation"])
            
        return template
        
    def _format_policy_guidance(self, template, data):
        """Format policy guidance response"""
        # Transfer relevant fields
        if "topic" in data:
            template["topic"] = data["topic"]
        if "guidance" in data:
            template["guidance"] = data["guidance"]
        if "key_points" in data:
            template["key_points"] = data["key_points"]
        elif "guidance" in data:
            # Extract key points from guidance
            template["key_points"] = self._extract_key_points(data["guidance"])
            
        # Extract citations
        if "citations" in data:
            template["citations"] = data["citations"]
        elif "guidance" in data:
            template["citations"] = self._extract_citations(data["guidance"])
            
        # Calculate confidence score
        template["confidence_score"] = self._calculate_confidence_score(data)
        
        # Related policies
        if "related_policies" in data:
            template["related_policies"] = data["related_policies"]
            
        # Generate concise summary
        if "guidance" in data:
            template["summary"] = self._generate_summary(data["guidance"])
            
        return template
        
    def _format_service_recommendation(self, template, data, original_data=None):
        """Format service recommendation response"""
        # Transfer key fields
        if "needs_addressed" in data:
            template["needs_addressed"] = data["needs_addressed"]
        elif original_data and "needs_description" in original_data:
            # Extract needs from original request
            template["needs_addressed"] = [original_data["needs_description"]]
            
        if "recommended_services" in data:
            template["recommended_services"] = data["recommended_services"]
        if "support_categories" in data:
            template["support_categories"] = data["support_categories"]
        if "rationale" in data:
            template["rationale"] = data["rationale"]
            
        # Extract citations
        if "citations" in data:
            template["citations"] = data["citations"]
        elif "rationale" in data:
            template["citations"] = self._extract_citations(data["rationale"])
            
        # Calculate confidence score
        template["confidence_score"] = self._calculate_confidence_score(data)
        
        # Generate concise summary
        if "rationale" in data:
            template["summary"] = self._generate_summary(data["rationale"])
            
        return template
        
    def _format_ndis_updates(self, template, data):
        """Format NDIS updates response"""
        # Transfer key fields
        if "update_period" in data:
            template["update_period"] = data["update_period"]
        if "updates" in data:
            template["updates"] = data["updates"]
        if "impact_assessment" in data:
            template["impact_assessment"] = data["impact_assessment"]
            
        # Extract citations
        if "citations" in data:
            template["citations"] = data["citations"]
        else:
            all_text = ""
            if "updates" in data and isinstance(data["updates"], list):
                for update in data["updates"]:
                    if isinstance(update, dict) and "description" in update:
                        all_text += update["description"] + " "
            if "impact_assessment" in data:
                all_text += data["impact_assessment"]
                
            template["citations"] = self._extract_citations(all_text)
            
        # Calculate confidence score
        template["confidence_score"] = self._calculate_confidence_score(data)
        
        # Generate concise summary
        summary_text = ""
        if "updates" in data and isinstance(data["updates"], list) and len(data["updates"]) > 0:
            summary_text = "Recent NDIS updates include: "
            for i, update in enumerate(data["updates"][:3]):  # Limit to top 3
                if isinstance(update, dict) and "title" in update:
                    summary_text += update["title"]
                    if i < min(2, len(data["updates"]) - 1):
                        summary_text += ", "
            template["summary"] = summary_text
            
        return template
        
    def _format_budget_planning(self, template, data, original_data=None):
        """Format budget planning response"""
        # Transfer key fields
        if original_data and "plan_amount" in original_data:
            template["total_amount"] = float(original_data["plan_amount"])
        if "allocations" in data:
            template["allocations"] = data["allocations"]
        if "rationale" in data:
            template["rationale"] = data["rationale"]
        if "notes" in data:
            template["notes"] = data["notes"]
            
        # Calculate confidence score
        template["confidence_score"] = self._calculate_confidence_score(data)
        
        # Generate concise summary
        if "allocations" in data and isinstance(data["allocations"], list):
            summary = f"Budget plan allocating ${template['total_amount']:,.2f} across {len(data['allocations'])} support categories"
            template["summary"] = summary
            
        return template
    
    def _extract_citations(self, text):
        """Extract URLs as citations from text"""
        if not text:
            return []
            
        # Match URLs in text
        url_pattern = r'https?://[^\s)>]+'
        urls = re.findall(url_pattern, text)
        
        # Format as citation objects
        citations = []
        for i, url in enumerate(urls):
            citations.append({
                "url": url,
                "source": self._extract_domain(url),
                "accessed_at": datetime.now().isoformat()
            })
            
        return citations
        
    def _extract_domain(self, url):
        """Extract domain name from URL"""
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            return domain_match.group(1)
        return "Unknown source"
        
    def _extract_key_points(self, text, max_points=3):
        """Extract key points from a longer text"""
        if not text:
            return []
            
        # Split by paragraphs or sentences
        paragraphs = re.split(r'\n\n|\.\s+', text)
        
        # Filter out short or incomplete sentences
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 30]
        
        # Return up to max_points paragraphs
        return paragraphs[:max_points]
        
    def _calculate_confidence_score(self, data):
        """Calculate a confidence score based on data quality"""
        score = 0.5  # Start with neutral score
        
        # Check for presence of citations (increases confidence)
        if "citations" in data and data["citations"]:
            score += 0.2
            
        # Check for official NDIS domain citations (high confidence)
        if "citations" in data and any("ndis.gov.au" in str(c) for c in data["citations"]):
            score += 0.15
            
        # Check for recency of information
        if "last_updated" in data:
            try:
                last_updated = datetime.fromisoformat(data["last_updated"])
                days_old = (datetime.now() - last_updated).days
                if days_old < 30:
                    score += 0.1
                elif days_old > 365:
                    score -= 0.1
            except:
                pass
                
        # Limit score to range [0.1, 0.95]
        return max(0.1, min(0.95, score))
        
    def _generate_summary(self, text, max_length=80):
        """Generate a concise summary from longer text"""
        if not text:
            return ""
            
        # Take first sentence if it's not too long
        first_sentence = re.split(r'(?<=\.)\s+', text)[0]
        if len(first_sentence) <= max_length:
            return first_sentence
            
        # Otherwise truncate with ellipsis
        return first_sentence[:max_length-3] + "..."
        
    def _clean_chain_of_thought(self, text):
        """
        Clean up Chain of Thought patterns from reasoning models
        
        Args:
            text (str): The text that may contain CoT patterns
            
        Returns:
            str: Cleaned text with CoT patterns removed
        """
        if not text:
            return text
            
        # First try to remove entire <think>...</think> blocks
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # If that didn't change anything, try removing just the tags
        cleaned = re.sub(r'</?think>', '', cleaned, flags=re.IGNORECASE)
            
        # Remove any double newlines created by the cleanup
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
        
    def add_confidence_indicator(self, response):
        """
        Add a human-readable confidence indicator based on score
        
        Args:
            response (dict): Formatted response with confidence_score
            
        Returns:
            dict: Response with added confidence_indicator
        """
        if "confidence_score" not in response:
            return response
            
        score = response["confidence_score"]
        
        if score >= 0.8:
            indicator = "High confidence"
        elif score >= 0.6:
            indicator = "Moderate confidence"
        elif score >= 0.4:
            indicator = "Standard confidence"
        else:
            indicator = "Low confidence - please verify"
            
        response["confidence_indicator"] = indicator
        return response
        
    def mark_outdated_information(self, response, threshold_days=365):
        """
        Mark potentially outdated information
        
        Args:
            response (dict): Formatted response
            threshold_days (int): Number of days after which to consider outdated
            
        Returns:
            dict: Response with outdated warnings if necessary
        """
        if "citations" not in response or not response["citations"]:
            # No citations to check recency
            response["warning"] = "No citations available - information may be outdated"
            return response
            
        # Check citation dates if available
        has_recent_citation = False
        for citation in response["citations"]:
            if "accessed_at" in citation:
                try:
                    accessed_at = datetime.fromisoformat(citation["accessed_at"])
                    days_ago = (datetime.now() - accessed_at).days
                    if days_ago < threshold_days:
                        has_recent_citation = True
                        break
                except:
                    pass
                    
        if not has_recent_citation:
            response["warning"] = f"Information may be outdated (no citations newer than {threshold_days} days)"
            
        return response
