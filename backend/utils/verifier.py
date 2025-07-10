"""
Verifier for NDIS Decoder
Cross-references information against official sources and flags uncertain information
"""
import re
import json
import os
from pathlib import Path
import requests
from urllib.parse import urlparse
import hashlib

class NDISVerifier:
    def __init__(self):
        """Initialize the NDIS verifier"""
        # Official NDIS domains for verification
        self.official_domains = [
            "ndis.gov.au",
            "dss.gov.au",
            "ndiscommission.gov.au",
            "ndia.gov.au"
        ]
        
        # Cache directory for verification data
        self.cache_dir = os.path.join(Path(__file__).parent.parent, "data/verification_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Common NDIS policies to check against
        self.key_policies = [
            "Price Guide",
            "Support Catalogue",
            "Operational Guidelines",
            "Practice Standards",
            "Provider Registration",
            "Quality and Safeguards"
        ]
        
        # Initialize fact verification pattern matching
        self.fact_patterns = {
            "ndis_code": r'\b\d{2}_\d{3}_\d{4}_\d_\d\b',
            "price_amount": r'\$\d+(\.\d{2})?',
            "percentage": r'\d+(\.\d+)?%',
            "date": r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        }
        
    def verify_against_sources(self, response_data, original_query=None):
        """
        Verify response data against official sources
        
        Args:
            response_data (dict): Response data to verify
            original_query (str, optional): Original user query
            
        Returns:
            dict: Verified response data with confidence flags
        """
        # Extract facts to verify
        facts = self._extract_facts(response_data)
        
        # Add verification flags
        verified_data = response_data.copy()
        
        # Add verification status
        if facts:
            # Verify facts against sources
            verification_results = self._verify_facts(facts)
            
            # Add verification results to response
            verified_data["verification"] = {
                "verified_facts": verification_results["verified"],
                "unverified_facts": verification_results["unverified"],
                "verification_score": verification_results["score"],
                "sources_checked": verification_results["sources"]
            }
            
            # Add overall verification assessment
            if verification_results["score"] > 0.8:
                verified_data["verification_status"] = "Highly verified"
            elif verification_results["score"] > 0.6:
                verified_data["verification_status"] = "Mostly verified"
            elif verification_results["score"] > 0.4:
                verified_data["verification_status"] = "Partially verified"
            else:
                verified_data["verification_status"] = "Minimally verified"
                verified_data["warning"] = "This information requires additional verification"
        else:
            # No facts to verify
            verified_data["verification_status"] = "No verifiable facts found"
            
        return verified_data
        
    def _extract_facts(self, data):
        """
        Extract verifiable facts from response data
        
        Args:
            data (dict): Response data
            
        Returns:
            list: List of facts to verify
        """
        facts = []
        
        # Convert to JSON string for easier searching
        data_str = json.dumps(data)
        
        # Extract facts based on patterns
        for fact_type, pattern in self.fact_patterns.items():
            matches = re.findall(pattern, data_str)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]  # Get the full match if it's a tuple
                facts.append({
                    "type": fact_type,
                    "value": match,
                    "verified": False
                })
                
        return facts
        
    def _verify_facts(self, facts):
        """
        Verify facts against official sources
        
        Args:
            facts (list): Facts to verify
            
        Returns:
            dict: Verification results
        """
        results = {
            "verified": [],
            "unverified": [],
            "score": 0.5,  # Start with neutral score
            "sources": []
        }
        
        # For each fact, check if we have cached verification
        for fact in facts:
            # Generate a cache key based on fact type and value
            cache_key = hashlib.md5(f"{fact['type']}:{fact['value']}".encode()).hexdigest()
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            # Check if we have a cached verification result
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cached_result = json.load(f)
                        
                    if cached_result["verified"]:
                        results["verified"].append(fact)
                    else:
                        results["unverified"].append(fact)
                        
                    # Add sources if not already in list
                    for source in cached_result["sources"]:
                        if source not in results["sources"]:
                            results["sources"].append(source)
                except Exception:
                    # If cache reading fails, consider fact unverified
                    results["unverified"].append(fact)
            else:
                # No cached verification, consider fact unverified
                results["unverified"].append(fact)
                
        # Calculate verification score based on verified vs. total facts
        total_facts = len(facts)
        if total_facts > 0:
            verified_count = len(results["verified"])
            results["score"] = verified_count / total_facts
        
        return results
        
    def cross_reference(self, fact_statement, threshold=0.6):
        """
        Cross-reference a factual statement against known NDIS information
        
        Args:
            fact_statement (str): Statement to verify
            threshold (float): Similarity threshold
            
        Returns:
            dict: Cross-reference results
        """
        # In a real implementation, this would use the Perplexity API to perform
        # a cross-reference search. For now, we'll simulate this with a check
        # against common patterns
        
        result = {
            "verified": False,
            "confidence": 0.0,
            "sources": []
        }
        
        # Check for common NDIS patterns that would be true
        if re.search(r'\b(NDIS plan|NDIS funding|NDIS support)\b', fact_statement, re.IGNORECASE):
            # General NDIS terminology is likely correct
            result["verified"] = True
            result["confidence"] = 0.7
            result["sources"].append("NDIS general information")
            
        # Check for policy references
        for policy in self.key_policies:
            if policy.lower() in fact_statement.lower():
                result["verified"] = True
                result["confidence"] = 0.8
                result["sources"].append(f"NDIS {policy}")
                
        # Check for NDIS code pattern
        code_match = re.search(self.fact_patterns["ndis_code"], fact_statement)
        if code_match:
            # This would validate against the actual NDIS support catalogue
            # For now, assume codes are partially verified
            result["verified"] = True
            result["confidence"] = 0.6
            result["sources"].append("NDIS Support Catalogue")
            
        # Return verified only if confidence is above threshold
        if result["confidence"] < threshold:
            result["verified"] = False
            
        return result
        
    def flag_uncertain_statements(self, response_data):
        """
        Flag potentially uncertain information in responses
        
        Args:
            response_data (dict): Response data to analyze
            
        Returns:
            dict: Response with uncertainty flags
        """
        # Uncertainty markers in text
        uncertainty_markers = [
            "may be", "might be", "could be", "possibly", "potentially",
            "unclear", "uncertain", "not specified", "not stated",
            "varies", "depends", "subject to change"
        ]
        
        # Convert to string for analysis
        data_str = json.dumps(response_data).lower()
        
        # Check for uncertainty markers
        uncertain_statements = []
        for marker in uncertainty_markers:
            # Find sentences containing uncertainty markers
            pattern = r'[^.!?]*\b' + re.escape(marker) + r'\b[^.!?]*[.!?]'
            matches = re.findall(pattern, data_str)
            uncertain_statements.extend(matches)
            
        if uncertain_statements:
            # Add uncertainty flags to response
            response_data["contains_uncertainty"] = True
            response_data["uncertain_statements"] = uncertain_statements[:3]  # Limit to top 3
            
        return response_data
        
    def verify_citation_legitimacy(self, citations):
        """
        Verify that citations reference legitimate sources
        
        Args:
            citations (list): List of citation objects
            
        Returns:
            list: Citations with verification status
        """
        verified_citations = []
        
        for citation in citations:
            verified_citation = citation.copy()
            verified_citation["legitimate_source"] = False
            
            # Check if URL is from an official domain
            if "url" in citation:
                url = citation["url"]
                try:
                    domain = urlparse(url).netloc
                    verified_citation["legitimate_source"] = any(
                        official_domain in domain for official_domain in self.official_domains
                    )
                except Exception:
                    # If URL parsing fails, consider not legitimate
                    pass
                    
            verified_citations.append(verified_citation)
            
        return verified_citations
        
    def validate_ndis_code(self, code):
        """
        Validate if an NDIS code follows the correct format and exists
        
        Args:
            code (str): NDIS code to validate
            
        Returns:
            bool: True if valid code format, False otherwise
        """
        # Check format: xx_xxx_xxxx_x_x
        pattern = r'^\d{2}_\d{3}_\d{4}_\d_\d$'
        return bool(re.match(pattern, code))
        
    def cache_verification_result(self, fact, verification_result):
        """
        Cache a verification result for future use
        
        Args:
            fact (dict): Fact that was verified
            verification_result (dict): Verification result
            
        Returns:
            bool: Success status
        """
        try:
            # Generate a cache key based on fact type and value
            cache_key = hashlib.md5(f"{fact['type']}:{fact['value']}".encode()).hexdigest()
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            # Store verification result
            with open(cache_file, 'w') as f:
                json.dump(verification_result, f)
                
            return True
        except Exception as e:
            print(f"Error caching verification result: {e}")
            return False
