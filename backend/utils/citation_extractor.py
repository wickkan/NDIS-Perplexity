"""
Citation Extractor for NDIS Decoder
Extracts and formats citations from Perplexity Sonar API responses
"""
import re
import json
from datetime import datetime
from urllib.parse import urlparse

class CitationExtractor:
    def __init__(self):
        """Initialize the citation extractor"""
        # Patterns for extracting citations in different formats
        self.citation_patterns = [
            # Pattern for URLs
            r'https?://[^\s)>]+',
            # Pattern for citation blocks [1]: http://...
            r'\[\d+\]:\s*(https?://[^\s)>]+)',
            # Pattern for footnotes with URLs
            r'\[\^?\d+\](?:[^[]*?)(https?://[^\s)>]+)',
            # Pattern for citation in parentheses (http://...)
            r'\((?:Source|Reference|Citation)?:?\s*(https?://[^\s)>]+)\)',
            # Pattern for "Source:" followed by URL
            r'Source(?:s)?:?\s*(https?://[^\s)>]+)',
            # Pattern for "Reference:" followed by URL
            r'Reference(?:s)?:?\s*(https?://[^\s)>]+)',
            # Pattern for "Citation:" followed by URL
            r'Citation(?:s)?:?\s*(https?://[^\s)>]+)'
        ]
        
        # Official NDIS domains for source verification
        self.official_domains = [
            "ndis.gov.au",
            "dss.gov.au",
            "ndiscommission.gov.au",
            "ndia.gov.au"
        ]
        
    def extract_citations(self, text):
        """
        Extract citations from text using multiple patterns
        
        Args:
            text (str): Text to extract citations from
            
        Returns:
            list: List of citation objects
        """
        if not text:
            return []
            
        all_urls = []
        
        # Try each pattern
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # If the match is a tuple (from a capturing group), take the first element
                url = match[0] if isinstance(match, tuple) else match
                url = url.strip()
                if url and url not in all_urls:
                    all_urls.append(url)
        
        # Format as citation objects
        citations = []
        for url in all_urls:
            domain = self._extract_domain(url)
            is_official = any(official in domain for official in self.official_domains)
            
            citations.append({
                "url": url,
                "source": domain,
                "accessed_at": datetime.now().isoformat(),
                "is_official_source": is_official
            })
            
        return citations
    
    def extract_citations_from_json(self, json_response):
        """
        Extract citations from Perplexity Sonar JSON response
        
        Args:
            json_response: JSON response from Perplexity API
            
        Returns:
            list: List of citation objects
        """
        citations = []
        
        try:
            # Try to extract citations from the response metadata (Perplexity Sonar-specific format)
            if hasattr(json_response, 'choices') and json_response.choices:
                # Check for citations in message metadata
                message = json_response.choices[0].message
                
                # Method 1: Extract from metadata citations field
                if hasattr(message, 'metadata') and message.metadata:
                    if 'citations' in message.metadata:
                        for citation in message.metadata['citations']:
                            if 'url' in citation:
                                domain = self._extract_domain(citation['url'])
                                is_official = any(official in domain for official in self.official_domains)
                                
                                citations.append({
                                    "url": citation['url'],
                                    "source": domain,
                                    "title": citation.get('title', domain),
                                    "accessed_at": datetime.now().isoformat(),
                                    "is_official_source": is_official
                                })
                    
                    # Perplexity API sometimes puts citations in 'sources' field
                    elif 'sources' in message.metadata:
                        for source in message.metadata['sources']:
                            if isinstance(source, dict) and 'url' in source:
                                domain = self._extract_domain(source['url'])
                                is_official = any(official in domain for official in self.official_domains)
                                
                                citations.append({
                                    "url": source['url'],
                                    "source": domain,
                                    "title": source.get('title', domain),
                                    "accessed_at": datetime.now().isoformat(),
                                    "is_official_source": is_official
                                })
                
                # Method 2: Extract from content.links field
                if hasattr(message, 'content_links') and message.content_links:
                    for link in message.content_links:
                        if 'url' in link:
                            domain = self._extract_domain(link['url'])
                            is_official = any(official in domain for official in self.official_domains)
                            
                            citations.append({
                                "url": link['url'],
                                "source": domain,
                                "title": link.get('title', domain),
                                "accessed_at": datetime.now().isoformat(),
                                "is_official_source": is_official
                            })
            
            # Method 3: If no citations found in metadata or links, try extracting from text
            if not citations and hasattr(json_response, 'choices') and json_response.choices:
                text = json_response.choices[0].message.content
                
                # First check for citation blocks in the text - Perplexity often adds these at the end
                citation_section = self._extract_citation_section(text)
                if citation_section:
                    # Extract citations from the dedicated section
                    section_citations = self.extract_citations(citation_section)
                    if section_citations:
                        citations.extend(section_citations)
                else:
                    # Fall back to extracting from the full text
                    citations = self.extract_citations(text)
                
        except Exception as e:
            print(f"Error extracting citations from JSON: {e}")
            # Fallback to empty list
            
        return citations
        
    def _extract_citation_section(self, text):
        """
        Extract the citation section from text if present
        
        Args:
            text (str): Full text content
            
        Returns:
            str: Citation section or None if not found
        """
        # Common section headers used by Perplexity
        section_headers = [
            r'\n\n[Ss]ources:\s*\n',
            r'\n\n[Cc]itations:\s*\n',
            r'\n\n[Rr]eferences:\s*\n',
            r'### [Ss]ources\s*\n',
            r'### [Cc]itations\s*\n',
            r'\*\*[Ss]ources\*\*\s*\n',
            r'\*\*[Cc]itations\*\*\s*\n'
        ]
        
        for header_pattern in section_headers:
            match = re.search(header_pattern, text)
            if match:
                # Get text from the header to the end
                start_idx = match.start()
                return text[start_idx:]
                
        return None
        
    def _extract_domain(self, url):
        """Extract domain name from URL"""
        try:
            domain = urlparse(url).netloc
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "Unknown source"
            
    def format_citations_for_display(self, citations):
        """
        Format citations for display
        
        Args:
            citations (list): List of citation objects
            
        Returns:
            str: Formatted citations string
        """
        if not citations:
            return "No citations available"
            
        formatted = []
        for i, citation in enumerate(citations, 1):
            source = citation.get('source', 'Unknown source')
            url = citation.get('url', '')
            title = citation.get('title', source)
            
            formatted.append(f"[{i}] {title}: {url}")
            
        return "\n".join(formatted)
        
    def extract_source_titles(self, text):
        """
        Extract source titles from text
        
        Args:
            text (str): Text to extract source titles from
            
        Returns:
            list: List of source titles
        """
        if not text:
            return []
            
        # Pattern for source titles
        patterns = [
            r'Source(?:s)?:?\s*"([^"]+)"',
            r'Reference(?:s)?:?\s*"([^"]+)"',
            r'Citation(?:s)?:?\s*"([^"]+)"',
            r'from\s+([^,\.]+)'
        ]
        
        titles = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            titles.extend(matches)
            
        return titles
