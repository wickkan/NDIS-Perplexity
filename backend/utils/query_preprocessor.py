"""
Query Preprocessor for NDIS Decoder
Handles domain-specific NDIS terminology and query enhancement
"""
import re
import json
import os
from pathlib import Path

class NDISQueryPreprocessor:
    def __init__(self):
        """Initialize the NDIS query preprocessor with domain-specific knowledge"""
        self.terminology_path = os.path.join(Path(__file__).parent.parent, "data/ndis_terminology.json")
        self.common_codes_path = os.path.join(Path(__file__).parent.parent, "data/common_ndis_codes.json")
        
        # Load NDIS terminology and common codes
        self.terminology = self._load_json(self.terminology_path, default={
            "acronyms": {
                "SIL": "Supported Independent Living",
                "SDA": "Specialist Disability Accommodation",
                "LAC": "Local Area Coordinator",
                "ECEI": "Early Childhood Early Intervention",
                "AT": "Assistive Technology",
                "SIL": "Supported Independent Living"
            },
            "common_terms": {
                "plan": "NDIS plan",
                "participant": "NDIS participant",
                "funding": "NDIS funding",
                "provider": "NDIS provider",
                "support": "NDIS support"
            }
        })
        
        self.common_codes = self._load_json(self.common_codes_path, default={
            "01_xxx_xxxx_x_x": "Core Supports",
            "03_xxx_xxxx_x_x": "Capacity Building",
            "04_xxx_xxxx_x_x": "Capital Supports",
            "01_011_xxxx_x_x": "Assistance with Daily Life"
        })
        
    def _load_json(self, file_path, default=None):
        """Load a JSON file, creating it with default values if it doesn't exist"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Create the file with default content
                if default:
                    with open(file_path, 'w') as f:
                        json.dump(default, f, indent=2)
                    return default
                return {}
        except Exception as e:
            print(f"Error loading terminology: {e}")
            return default or {}
            
    def _update_terminology(self, new_terms):
        """Update terminology database with new terms"""
        try:
            self.terminology.update(new_terms)
            with open(self.terminology_path, 'w') as f:
                json.dump(self.terminology, f, indent=2)
            return True
        except Exception as e:
            print(f"Error updating terminology: {e}")
            return False
    
    def expand_acronyms(self, query):
        """Expand NDIS-specific acronyms in the query"""
        expanded = query
        for acronym, full_form in self.terminology.get("acronyms", {}).items():
            # Match whole word acronyms only
            pattern = r'\b' + re.escape(acronym) + r'\b'
            expanded = re.sub(pattern, f"{acronym} ({full_form})", expanded)
        return expanded
        
    def correct_ndis_code_format(self, query):
        """Correct common NDIS code format errors"""
        # Match potential NDIS codes with incorrect formatting
        patterns = [
            # Match patterns like 01.011.0123.1.1 and convert to 01_011_0123_1_1
            (r'(\d{2})\.(\d{3})\.(\d{4})\.(\d)\.(\d)', r'\1_\2_\3_\4_\5'),
            # Match patterns like 01-011-0123-1-1 and convert to 01_011_0123_1_1
            (r'(\d{2})\-(\d{3})\-(\d{4})\-(\d)\-(\d)', r'\1_\2_\3_\4_\5'),
            # Match incomplete codes like 01011 and suggest completion
            (r'\b(\d{2})(\d{3})\b', r'\1_\2_xxxx_x_x')
        ]
        
        corrected = query
        for pattern, replacement in patterns:
            corrected = re.sub(pattern, replacement, corrected)
            
        return corrected
        
    def enhance_query(self, query, query_type="general"):
        """
        Enhance the query with domain-specific knowledge
        
        Args:
            query (str): Original user query
            query_type (str): Type of query (policy, service, etc.)
            
        Returns:
            str: Enhanced query
        """
        # Apply basic preprocessing
        enhanced = query.strip()
        
        # Expand acronyms
        enhanced = self.expand_acronyms(enhanced)
        
        # Correct NDIS code formats
        enhanced = self.correct_ndis_code_format(enhanced)
        
        # Add context based on query type
        if query_type == "policy":
            enhanced = f"NDIS policy question: {enhanced}"
        elif query_type == "service":
            enhanced = f"NDIS service question: {enhanced}"
        elif query_type == "budget":
            enhanced = f"NDIS budget planning question: {enhanced}"
            
        return enhanced
        
    def extract_key_entities(self, query):
        """
        Extract key entities from the query (support categories, codes, etc.)
        
        Args:
            query (str): User query
            
        Returns:
            dict: Dictionary of extracted entities
        """
        entities = {
            "support_categories": [],
            "ndis_codes": [],
            "participant_needs": []
        }
        
        # Extract NDIS codes (format: xx_xxx_xxxx_x_x)
        code_pattern = r'\b\d{2}_\d{3}_\d{4}_\d_\d\b'
        entities["ndis_codes"] = re.findall(code_pattern, query)
        
        # Extract support categories (simplified)
        support_categories = ["Daily Life", "Social", "Transport", "Home", 
                            "Health", "Therapy", "Equipment", "Capacity Building"]
        for category in support_categories:
            if re.search(r'\b' + re.escape(category) + r'\b', query, re.IGNORECASE):
                entities["support_categories"].append(category)
                
        return entities
        
    def log_and_learn(self, query, successful_response=None):
        """
        Log queries to improve future preprocessing
        
        Args:
            query (str): Original user query
            successful_response (dict, optional): If provided, used to extract new learning
            
        Returns:
            bool: Success status
        """
        try:
            # For now, just log queries
            log_dir = os.path.join(Path(__file__).parent.parent, "data/query_logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # Append to log file
            with open(os.path.join(log_dir, "query_log.txt"), 'a') as f:
                f.write(f"{query}\n")
                
            return True
        except Exception as e:
            print(f"Error logging query: {e}")
            return False
