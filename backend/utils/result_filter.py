"""
Result Filter for NDIS Decoder
Implements intelligent filtering and prioritization of results
"""
import re
import json
from datetime import datetime

class NDISResultFilter:
    def __init__(self):
        """Initialize the NDIS result filter"""
        # Define relevance scoring criteria
        self.relevance_criteria = {
            "official_source": 2.0,     # Official NDIS sources
            "recency": 1.5,             # Recent information
            "specificity": 1.2,         # Specific to the query
            "local_relevance": 1.3      # Relevant to user's state/region
        }
        
        # Official NDIS domains for source verification
        self.official_domains = [
            "ndis.gov.au",
            "dss.gov.au",
            "ndiscommission.gov.au",
            "ndia.gov.au"
        ]
        
        # Terms indicating outdated information
        self.outdated_terms = [
            "previous scheme",
            "has been replaced",
            "no longer valid",
            "discontinued",
            "prior to 2023"
        ]
        
    def filter_results(self, response_data, user_region=None, max_items=5):
        """
        Filter and prioritize results
        
        Args:
            response_data (dict): Response data to filter
            user_region (str, optional): User's state or region
            max_items (int): Maximum number of items to include
            
        Returns:
            dict: Filtered response data
        """
        # Apply different filtering based on response structure
        if "support_codes" in response_data and isinstance(response_data["support_codes"], list):
            response_data["support_codes"] = self._filter_support_codes(
                response_data["support_codes"], 
                user_region, 
                max_items
            )
            
        if "recommended_services" in response_data and isinstance(response_data["recommended_services"], list):
            response_data["recommended_services"] = self._filter_services(
                response_data["recommended_services"], 
                user_region, 
                max_items
            )
            
        if "updates" in response_data and isinstance(response_data["updates"], list):
            response_data["updates"] = self._filter_updates(
                response_data["updates"], 
                max_items
            )
            
        if "citations" in response_data and isinstance(response_data["citations"], list):
            response_data["citations"] = self._filter_citations(
                response_data["citations"], 
                max_items
            )
            
        return response_data
        
    def _filter_support_codes(self, support_codes, user_region=None, max_items=5):
        """Filter and prioritize support codes"""
        if not support_codes:
            return []
            
        # Score each code for relevance
        scored_codes = []
        for code in support_codes:
            score = 1.0  # Base score
            
            # Check if code has price for user's region
            if user_region and isinstance(code, dict):
                if user_region in code:
                    score *= self.relevance_criteria["local_relevance"]
                    
            # Check for specificity (presence of detailed description)
            if isinstance(code, dict) and "description" in code and len(code.get("description", "")) > 50:
                score *= self.relevance_criteria["specificity"]
                
            scored_codes.append((score, code))
            
        # Sort by score and take top max_items
        scored_codes.sort(reverse=True, key=lambda x: x[0])
        return [code for _, code in scored_codes[:max_items]]
        
    def _filter_services(self, services, user_region=None, max_items=5):
        """Filter and prioritize recommended services"""
        if not services:
            return []
            
        # Score each service for relevance
        scored_services = []
        for service in services:
            score = 1.0  # Base score
            
            # Check if service is region-specific
            if user_region and isinstance(service, dict):
                service_text = json.dumps(service).lower()
                if user_region.lower() in service_text:
                    score *= self.relevance_criteria["local_relevance"]
                    
            # Check for specificity (presence of detailed description)
            if isinstance(service, dict) and "description" in service and len(service.get("description", "")) > 50:
                score *= self.relevance_criteria["specificity"]
                
            # Check for official reference
            if isinstance(service, dict) and "reference" in service:
                ref = service["reference"].lower()
                if any(domain in ref for domain in self.official_domains):
                    score *= self.relevance_criteria["official_source"]
                    
            scored_services.append((score, service))
            
        # Sort by score and take top max_items
        scored_services.sort(reverse=True, key=lambda x: x[0])
        return [service for _, service in scored_services[:max_items]]
        
    def _filter_updates(self, updates, max_items=5):
        """Filter and prioritize NDIS updates"""
        if not updates:
            return []
            
        # Score each update for relevance
        scored_updates = []
        for update in updates:
            score = 1.0  # Base score
            
            # Check for recency
            if isinstance(update, dict) and "date" in update:
                try:
                    update_date = datetime.fromisoformat(update["date"])
                    days_old = (datetime.now() - update_date).days
                    if days_old < 30:
                        score *= self.relevance_criteria["recency"]
                    elif days_old > 365:
                        score *= 0.5  # Penalize very old updates
                except Exception:
                    # If date parsing fails, don't modify score
                    pass
                    
            # Check for official source
            if isinstance(update, dict) and "source" in update:
                source = update["source"].lower()
                if any(domain in source for domain in self.official_domains):
                    score *= self.relevance_criteria["official_source"]
                    
            scored_updates.append((score, update))
            
        # Sort by score and take top max_items
        scored_updates.sort(reverse=True, key=lambda x: x[0])
        return [update for _, update in scored_updates[:max_items]]
        
    def _filter_citations(self, citations, max_items=5):
        """Filter and prioritize citations"""
        if not citations:
            return []
            
        # Score each citation for relevance
        scored_citations = []
        for citation in citations:
            score = 1.0  # Base score
            
            # Check for official sources
            if isinstance(citation, dict) and "url" in citation:
                url = citation["url"].lower()
                if any(domain in url for domain in self.official_domains):
                    score *= self.relevance_criteria["official_source"]
                    
            # Check for recency if available
            if isinstance(citation, dict) and "accessed_at" in citation:
                try:
                    access_date = datetime.fromisoformat(citation["accessed_at"])
                    days_old = (datetime.now() - access_date).days
                    if days_old < 7:
                        score *= self.relevance_criteria["recency"]
                except Exception:
                    # If date parsing fails, don't modify score
                    pass
                    
            scored_citations.append((score, citation))
            
        # Sort by score and take top max_items
        scored_citations.sort(reverse=True, key=lambda x: x[0])
        return [citation for _, citation in scored_citations[:max_items]]
        
    def highlight_region_specific(self, response_data, user_region):
        """
        Highlight information specific to user's region
        
        Args:
            response_data (dict): Response data
            user_region (str): User's state or region
            
        Returns:
            dict: Response with highlighted region-specific info
        """
        if not user_region:
            return response_data
            
        # Add a region_specific flag to relevant items
        if "support_codes" in response_data and isinstance(response_data["support_codes"], list):
            for code in response_data["support_codes"]:
                if isinstance(code, dict):
                    # Check if code has region-specific pricing
                    if user_region in code:
                        code["region_specific"] = True
                        # Highlight the relevant price
                        if "price_caps" in code and isinstance(code["price_caps"], dict):
                            code["highlighted_price"] = code["price_caps"].get(user_region)
                            
        if "recommended_services" in response_data and isinstance(response_data["recommended_services"], list):
            for service in response_data["recommended_services"]:
                if isinstance(service, dict):
                    # Check if service description mentions the region
                    service_text = json.dumps(service).lower()
                    if user_region.lower() in service_text:
                        service["region_specific"] = True
                        
        if "updates" in response_data and isinstance(response_data["updates"], list):
            for update in response_data["updates"]:
                if isinstance(update, dict) and "description" in update:
                    # Check if update mentions the region
                    if user_region.lower() in update["description"].lower():
                        update["region_specific"] = True
                        
        return response_data
        
    def filter_outdated_information(self, response_data):
        """
        Filter out obviously outdated information
        
        Args:
            response_data (dict): Response data
            
        Returns:
            dict: Response with outdated info removed or flagged
        """
        # Check for outdated support codes
        if "support_codes" in response_data and isinstance(response_data["support_codes"], list):
            filtered_codes = []
            for code in response_data["support_codes"]:
                if isinstance(code, dict) and "description" in code:
                    # Check if description contains outdated terms
                    desc = code["description"].lower()
                    is_outdated = any(term in desc for term in self.outdated_terms)
                    
                    if is_outdated:
                        code["outdated"] = True  # Flag as outdated but keep it
                    filtered_codes.append(code)
            response_data["support_codes"] = filtered_codes
            
        # Check for outdated updates
        if "updates" in response_data and isinstance(response_data["updates"], list):
            filtered_updates = []
            for update in response_data["updates"]:
                if isinstance(update, dict):
                    # Check update date if available
                    if "date" in update:
                        try:
                            update_date = datetime.fromisoformat(update["date"])
                            days_old = (datetime.now() - update_date).days
                            if days_old > 365:
                                update["outdated"] = True  # Flag as outdated but keep it
                        except Exception:
                            # If date parsing fails, check for outdated terms
                            if "description" in update:
                                desc = update["description"].lower()
                                is_outdated = any(term in desc for term in self.outdated_terms)
                                if is_outdated:
                                    update["outdated"] = True
                    filtered_updates.append(update)
            response_data["updates"] = filtered_updates
            
        return response_data
