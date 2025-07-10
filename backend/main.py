import os
import base64
import re
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import CitationExtractor

# Load environment variables
load_dotenv()


class NDISInvoiceDecoder:
    def __init__(self, api_key):
        """
        Initialize the NDIS Invoice Decoder with Perplexity Sonar API

        Args:
            api_key (str): Perplexity API key
        """
        self.client = OpenAI(
            api_key=api_key, base_url="https://api.perplexity.ai")
        self.ndis_data = self._load_ndis_data()
        self.citation_extractor = CitationExtractor()

    def encode_image(self, image_path):
        """
        Encode image to base64 for API processing

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Base64 encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _load_ndis_data(self):
        """
        Load NDIS support catalogue from Excel file

        Returns:
            DataFrame: NDIS Support Catalogue data
        """
        try:
            file_path = os.path.join(os.path.dirname(
                __file__), "data/NDIS_Support_Catalogue_2024_25.xlsx")
            df = pd.read_excel(file_path)
            if os.getenv('DEBUG') == 'True':
                print(f"Loaded NDIS data with {len(df)} support items")
            return df
        except Exception as e:
            if os.getenv('DEBUG') == 'True':
                print(f"ERROR loading NDIS data: {e}")
            return pd.DataFrame()

    def _find_matching_codes(self, description, top_n=5):
        """
        Find matching NDIS codes based on description using vector similarity

        Args:
            description (str): Service description to match
            top_n (int): Number of matches to return

        Returns:
            list: Top matching NDIS codes with details
        """
        # Create a temporary copy to avoid SettingWithCopyWarning
        temp_df = self.ndis_data.copy()

        # Feature engineering - create a combined text field for better matching
        temp_df['combined_text'] = temp_df['Support Item Name'].fillna('')
        if 'Support Category Name' in temp_df.columns:
            temp_df['combined_text'] += ' ' + \
                temp_df['Support Category Name'].fillna('')
        if 'Registration Group Name' in temp_df.columns:
            temp_df['combined_text'] += ' ' + \
                temp_df['Registration Group Name'].fillna('')

        # Convert to list for vectorization
        corpus = temp_df['combined_text'].tolist()

        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # Transform the query
        query_vec = vectorizer.transform([description])

        # Calculate similarity
        similarity = cosine_similarity(query_vec, tfidf_matrix)

        # Get top matches
        top_indices = similarity[0].argsort()[-top_n:][::-1]

        # Return matching codes
        matching_codes = []
        for idx in top_indices:
            if similarity[0][idx] > 0.1:  # Only include somewhat relevant matches
                matching_codes.append(temp_df.iloc[idx])

        return matching_codes

    def _format_price_caps(self, code_row):
        """
        Format price caps for different regions

        Args:
            code_row (Series): Row from NDIS data containing price information

        Returns:
            str: Formatted price cap string
        """
        price_caps = []

        # Add standard prices for each state
        for state in ['VIC', 'NSW', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']:
            if state in code_row and pd.notna(code_row[state]):
                price_caps.append(f"${code_row[state]} for {state}")

        # Add remote pricing if available
        if 'Remote' in code_row and pd.notna(code_row['Remote']):
            price_caps.append(f"${code_row['Remote']} for Remote area")

        # Add very remote pricing if available
        if 'Very Remote' in code_row and pd.notna(code_row['Very Remote']):
            price_caps.append(
                f"${code_row['Very Remote']} for Very Remote area")

        return ", ".join(price_caps) if price_caps else "Price not specified"

    def _extract_rules(self, code_row):
        """
        Extract rules and conditions for a support item

        Args:
            code_row (Series): Row from NDIS data

        Returns:
            str: Formatted rules string
        """
        rules = ["Price Limited Supports"]

        # Add special conditions
        fields = [
            ('Provider Travel', 'Provider Travel'),
            ('NDIA Requested Reports', 'NDIA Requested Reports'),
            ('Short Notice Cancellations.', 'Short Notice Cancellations'),
            ('Non-Face-to-Face Support Provision', 'Non-Face-to-Face Support')
        ]

        for col, label in fields:
            if col in code_row and pd.notna(code_row[col]) and code_row[col] == 'Y':
                rules.append(label + ": Yes")
            elif col in code_row and pd.notna(code_row[col]) and code_row[col] == 'N':
                rules.append(label + ": No")

        return ", ".join(rules)

    def _generate_concise_explanation(self, matching_codes, service_description):
        """
        Generate a concise explanation for the matched codes

        Args:
            matching_codes (list): List of matching code rows
            service_description (str): Original service description

        Returns:
            str: Concise explanation about the codes
        """
        # If no matches found
        if not matching_codes:
            return "No matching NDIS codes found for the provided description."

        try:
            # Get the top match for explanation
            top_match = matching_codes[0]

            # Safely access column values with error handling
            try:
                # Proper way to access pandas Series values with fallback
                item_number = top_match['Support Item Number'] if 'Support Item Number' in top_match else 'unknown code'
                item_name = top_match['Support Item Name'] if 'Support Item Name' in top_match else 'unknown service'

                # Create explanation based on best match
                explanation = (
                    f"Based on your description '{service_description}', the most relevant NDIS support code is "
                    f"{item_number} for {item_name}. "
                )

                # Add category information if available
                if 'Support Category Name' in top_match and pd.notna(top_match['Support Category Name']):
                    explanation += f"This falls under the {top_match['Support Category Name']} category. "

                # Add advice about multiple options if applicable
                if len(matching_codes) > 1:
                    explanation += ("Multiple NDIS codes could potentially apply depending on specific details. "
                                    "Please review all options to select the most appropriate code for your situation.")

                return explanation

            except (KeyError, TypeError) as e:
                if os.getenv('DEBUG') == 'True':
                    print(f"Error accessing dataframe column: {e}")
                return f"Found potential NDIS codes that match '{service_description}', but encountered an error with details. Please see the matched codes for more information."

        except Exception as e:
            if os.getenv('DEBUG') == 'True':
                print(f"Error generating explanation: {e}")
            return "Found potential matching NDIS codes. Please review the options provided."

    def decode_invoice(self, image_path=None, text_description=None):
        """
        Decode NDIS invoice using Perplexity Sonar API and NDIS database

        Args:
            image_path (str, optional): Path to invoice image
            text_description (str, optional): Textual description of invoice item

        Returns:
            dict: Decoded NDIS codes and explanations in a structured format
        """
        # Step 1: Use Sonar for initial interpretation to enhance matching
        try:
            # Internal logging only visible in backend logs
            if os.getenv('DEBUG') == 'True':
                print("Making API call to Perplexity Sonar...")
            # Prepare messages for Sonar API
            messages = []

            # Add system context for NDIS interpretation
            messages.append({
                "role": "system",
                "content": (
                    "You are an expert NDIS (National Disability Insurance Scheme) service classifier. "
                    "Your task is to understand the given invoice or description and provide a clear, detailed "
                    "interpretation of the service being described. Focus on identifying the type of service, "
                    "the support category, and any special conditions (like time of day, weekend service, etc). "
                    "Do NOT attempt to provide NDIS codes directly - just describe the service in detail."
                )
            })

            # Process image if provided
            if image_path:
                base64_image = self.encode_image(image_path)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this invoice and describe the service provided in detail."},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                })

            # Process text description if provided
            if text_description:
                messages.append({
                    "role": "user",
                    "content": f"Describe this service in detail to help identify the NDIS category: {text_description}"
                })

            # Call Sonar API for enhanced interpretation
            response = self.client.chat.completions.create(
                model="sonar",  # Using standard sonar model
                messages=messages,
                max_tokens=400,  # Reduced for more concise responses
                temperature=0.1  # Lower temperature for more focused responses
            )

            # Extract enhanced description
            enhanced_description = response.choices[0].message.content
            # Internal logging only visible in backend logs
            if os.getenv('DEBUG') == 'True':
                print(f"Enhanced description: {enhanced_description[:100]}...")

            # Step 2: Use the enhanced description to search our database
            search_text = enhanced_description
            if text_description:  # Add original description for better context
                search_text = text_description + " " + enhanced_description

            # Find matching codes from our database
            matching_codes = self._find_matching_codes(search_text)

            # Step 3: Format the results in a clean, structured way for the frontend
            formatted_results = []

            # Check if we have any matching codes
            if not matching_codes:
                if os.getenv('DEBUG') == 'True':
                    print("No matching codes found. Using generic response.")
                # Return a generic response if no matches found
                return {
                    "codes": [],
                    "formatted_results": ["No specific NDIS codes found for this description."],
                    "explanation": f"Could not find specific NDIS codes that match '{text_description or 'the description'}'. "
                    f"Please try providing more specific details about the service type."
                }

            for code_row in matching_codes:
                try:
                    item_code = code_row['Support Item Number']
                    description = code_row['Support Item Name']
                    price_cap = self._format_price_caps(code_row)
                    rules = self._extract_rules(code_row)

                    formatted_results.append(
                        f"Item Code: {item_code}\n"
                        f"Description: {description}\n"
                        f"Price Cap: {price_cap}\n"
                        f"Rules: {rules}"
                    )
                except Exception as e:
                    if os.getenv('DEBUG') == 'True':
                        print(f"Error formatting a result: {str(e)}")
                    # Continue with other results if one fails

            # Generate a concise explanation
            explanation = self._generate_concise_explanation(
                matching_codes, text_description or "")

            # Extract citations from the enhanced description
            citations = self._extract_citations(enhanced_description, response)

            # Return formatted result with all the information needed for the frontend
            return {
                "codes": [code_row['Support Item Number'] for code_row in matching_codes],
                "formatted_results": formatted_results,
                "explanation": explanation,
                "citations": citations
            }

        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            if os.getenv('DEBUG') == 'True':
                print(f"\nERROR: {error_msg}")
            return {
                "error": error_msg,
                "codes": [],
                "formatted_results": [],
                "explanation": "Error occurred during processing"
            }

    def _extract_citations(self, response_text, api_response=None):
        """
        Extract citations from Perplexity API response

        Args:
            response_text (str): Full API response text
            api_response (object, optional): Raw API response object

        Returns:
            list: Extracted citations as structured objects
        """
        # Use our enhanced citation extractor
        if api_response:
            # Try to extract from API response metadata first
            citations = self.citation_extractor.extract_citations_from_json(
                api_response)
            if citations:
                return citations

        # Fall back to text extraction if no citations found in metadata
        return self.citation_extractor.extract_citations(response_text)

    def get_ndis_policy_guidance(self, query, category=None):
        """
        Provide guidance on NDIS policies and rules

        Args:
            query (str): User's policy question
            category (str, optional): Specific policy category to focus on

        Returns:
            dict: Policy guidance with citations and related codes
        """
        # Prepare system prompt with specific policy expertise
        system_prompt = (
            "You are an NDIS policy expert specializing in providing clear, accurate guidance. "
            "Focus on practical implications for participants and providers. "
            "Always cite official NDIS documentation when possible. "
            "Structure your response with: 1) Direct answer to the question "
            "2) Relevant policy details 3) Practical implications 4) Related considerations"
        )

        # Add category context if provided
        if category:
            system_prompt += f" Focus specifically on {category} policies and guidelines."

        # Prepare user query with enhanced context
        user_query = f"Explain the NDIS policy regarding: {query}"

        # Add search context to ensure up-to-date information
        search_context = (
            "Before answering, search for the most recent NDIS price guide and policy documents. "
            "Ensure your answer reflects current NDIS policies as of May 2025."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{search_context}\n\n{user_query}"}
        ]

        # Call Sonar API with enhanced reasoning
        response = self.client.chat.completions.create(
            model="sonar",
            messages=messages,
            max_tokens=800,
            temperature=0.1  # Lower temperature for more focused responses
        )

        guidance_text = response.choices[0].message.content

        # Extract citations for verification
        citations = self._extract_citations(guidance_text, response)

        # Find related NDIS codes that might be relevant to this policy question
        related_codes = self._find_related_codes(query, limit=3)

        return {
            "guidance": guidance_text,
            "citations": citations,
            "related_codes": related_codes
        }

    def _find_related_codes(self, query, limit=3):
        """Find NDIS codes related to a policy question"""
        matching_codes = self._find_matching_codes(query, top_n=limit)
        return [{
            "code": code["Support Item Number"],
            "name": code["Support Item Name"]
        } for code in matching_codes if "Support Item Number" in code and "Support Item Name" in code]

    def recommend_services(self, needs_description, participant_details=None):
        """
        Recommend appropriate NDIS services based on described needs

        Args:
            needs_description (str): Description of participant's needs
            participant_details (dict, optional): Additional context about the participant

        Returns:
            dict: Recommended services with rationale and codes
        """
        # Build comprehensive context about the participant
        participant_context = "Based on the described needs"
        if participant_details:
            if participant_details.get('age'):
                participant_context += f", for a {participant_details['age']}-year-old participant"
            if participant_details.get('location'):
                participant_context += f" located in {participant_details['location']}"
            if participant_details.get('disability_type'):
                participant_context += f" with {participant_details['disability_type']}"

        # Create system prompt for service matching expertise
        system_prompt = (
            "You are an NDIS service matching expert with deep knowledge of available supports. "
            "Your task is to recommend the most appropriate NDIS services based on a participant's needs. "
            "For each recommendation, explain: 1) Why this service is appropriate "
            "2) How it addresses specific needs 3) What outcomes it aims to achieve "
            "4) Any considerations for implementation"
        )

        # Create detailed user query
        user_query = (
            f"{participant_context}, recommend the most appropriate NDIS services for: {needs_description}\n\n"
            "Focus on evidence-based supports that align with NDIS goals of independence and participation."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]

        # Call Sonar API for service recommendations
        response = self.client.chat.completions.create(
            model="sonar",
            messages=messages,
            max_tokens=1000,
            temperature=0.1  # Lower temperature for more focused responses
        )

        recommendation_text = response.choices[0].message.content

        # Extract citations
        citations = self._extract_citations(recommendation_text, response)

        # Extract key service types mentioned in the recommendation
        service_types = self._extract_service_types(recommendation_text)

        # Find matching NDIS codes for each recommended service type
        recommended_services = []
        for service_type in service_types:
            matching_codes = self._find_matching_codes(service_type, top_n=2)
            if matching_codes:
                for code in matching_codes:
                    if "Support Item Number" in code and "Support Item Name" in code:
                        recommended_services.append({
                            "service_type": service_type,
                            "code": code["Support Item Number"],
                            "name": code["Support Item Name"],
                            "price": self._format_price_caps(code)
                        })

        return {
            "recommendation": recommendation_text,
            "service_types": service_types,
            "recommended_codes": recommended_services,
            "citations": citations
        }

    def _extract_service_types(self, text):
        """Extract key service types from recommendation text"""
        # Use Sonar to extract the key service types
        messages = [
            {"role": "system", "content": "Extract the key NDIS service types mentioned in this text. Return only the service types as a comma-separated list."},
            {"role": "user", "content": text}
        ]

        response = self.client.chat.completions.create(
            model="sonar",
            messages=messages,
            max_tokens=200
        )

        service_types_text = response.choices[0].message.content
        service_types = [s.strip() for s in service_types_text.split(',')]
        return service_types

    def get_ndis_updates(self, focus_area=None, time_period="3 months"):
        """
        Get latest NDIS policy updates and news

        Args:
            focus_area (str, optional): Specific area to focus updates on (e.g., "pricing", "eligibility")
            time_period (str): Time period to look back for updates

        Returns:
            dict: Latest updates with sources and implications
        """
        # Create focused query based on parameters
        focus_query = ""
        if focus_area:
            focus_query = f" Focus specifically on updates related to {focus_area}."

        # System prompt for news analysis
        system_prompt = (
            "You are an NDIS news analyst specializing in monitoring and interpreting changes to NDIS policies, "
            "pricing, and procedures. Provide accurate, concise summaries of significant changes that affect "
            "service providers and participants directly. For each update, include: 1) The change 2) When it took effect "
            "3) Who it impacts 4) Practical implications 5) Source"
        )

        # User query with search instructions
        user_query = (
            f"What are the most significant changes to NDIS policies, pricing, or procedures in the last {time_period}?{focus_query} "
            "Search for the most recent information from official NDIS sources, news articles, and government announcements. "
            "Prioritize changes that have the biggest impact on service delivery or participant experience."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]

        # Call Sonar API with real-time search capabilities
        response = self.client.chat.completions.create(
            model="sonar",
            messages=messages,
            max_tokens=1000,
            temperature=0.1  # Lower temperature for more focused responses
        )

        updates_text = response.choices[0].message.content

        # Extract citations for verification
        sources = self._extract_citations(updates_text, response)

        # Extract key updates as structured data
        key_updates = self._extract_key_updates(updates_text)

        return {
            "updates_summary": updates_text,
            "sources": sources,
            "key_updates": key_updates,
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }

    def _extract_key_updates(self, text):
        """Extract structured key updates from the text"""
        # Use Sonar to extract structured updates
        messages = [
            {"role": "system", "content": "Extract the key NDIS updates from this text as a JSON array. Each update should have: title, effective_date, impact, and description fields."},
            {"role": "user", "content": text}
        ]

        response = self.client.chat.completions.create(
            model="sonar",
            messages=messages,
            max_tokens=500
        )

        try:
            # Try to parse as JSON
            updates_text = response.choices[0].message.content
            # Extract JSON from text (in case there's surrounding text)
            json_match = re.search(
                r'\[\s*\{.*\}\s*\]', updates_text, re.DOTALL)
            if json_match:
                updates_json = json.loads(json_match.group(0))
                return updates_json
        except Exception as e:
            if os.getenv('DEBUG') == 'True':
                print(f"Error parsing updates JSON: {e}")
            # Fallback to simple text parsing if JSON extraction fails
            updates = []
            sections = re.split(r'\n\s*\d+\.\s+', text)
            # Skip first empty split
            for i, section in enumerate(sections[1:], 1):
                updates.append({
                    "title": section.split('\n')[0] if section else f"Update {i}",
                    "description": section,
                    "id": i
                })
            return updates

    def plan_budget(self, plan_amount, needs_description, existing_supports=None, priorities=None):
        """
        Help allocate NDIS plan budget based on participant needs

        Args:
            plan_amount (float): Total NDIS plan budget amount
            needs_description (str): Description of participant's needs and goals
            existing_supports (list, optional): List of existing supports
            priorities (list, optional): Participant's priorities for support

        Returns:
            dict: Budget allocation recommendations with rationale
        """
        # Format existing supports context
        existing_context = ""
        if existing_supports:
            existing_context = "Current supports include: " + \
                ", ".join(existing_supports) + ". "

        # Format priorities context
        priorities_context = ""
        if priorities:
            priorities_context = "The participant's priorities are: " + \
                ", ".join(priorities) + ". "

        # System prompt for budget planning expertise
        system_prompt = (
            "You are an NDIS budget planning expert. Help participants allocate their NDIS funding effectively "
            "across different support categories based on their needs and goals. For each recommendation, explain: "
            "1) The recommended allocation 2) How it addresses specific needs 3) The expected outcomes "
            "4) Any flexibility considerations"
        )

        # User query with comprehensive context
        user_query = (
            f"Help allocate an NDIS plan budget of ${plan_amount:,.2f} based on these needs and goals: {needs_description}\n\n"
            f"{existing_context}{priorities_context}"
            "Provide a breakdown by support categories with specific recommended services and approximate costs. "
            "Ensure the total allocation matches the plan amount."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]

        # Call Sonar API for budget planning
        response = self.client.chat.completions.create(
            model="sonar",
            messages=messages,
            max_tokens=1200,
            temperature=0.1  # Lower temperature for more focused responses
        )

        # Generate budget allocation recommendations
        budget_text = response.choices[0].message.content

        # Extract structured budget allocation
        allocations = self._extract_budget_allocation(budget_text, plan_amount)

        # Extract citations
        citations = self._extract_citations(budget_text, response)

        # Find recommended NDIS codes for each support category
        recommended_codes = {}
        for category in allocations.keys():
            category_codes = self._find_matching_codes(category, top_n=3)
            if category_codes:
                recommended_codes[category] = [{
                    "code": code["Support Item Number"],
                    "name": code["Support Item Name"],
                    "price": self._format_price_caps(code)
                } for code in category_codes if "Support Item Number" in code and "Support Item Name" in code]

        return {
            "plan_amount": plan_amount,
            "allocation_summary": budget_text,
            "budget_allocation": allocations,
            "recommended_codes": recommended_codes,
            "citations": citations
        }

    def _extract_budget_allocation(self, text, plan_amount):
        """Extract structured budget allocation from the text"""
        # Use Sonar to extract structured budget allocation
        messages = [
            {"role": "system", "content": f"Extract the budget allocation from this text as a JSON object. The allocation should be for a total budget of ${plan_amount:,.2f} and include support categories as keys with amount and percentage values."},
            {"role": "user", "content": text}
        ]

        response = self.client.chat.completions.create(
            model="sonar",
            messages=messages,
            max_tokens=500
        )

        try:
            # Try to parse as JSON
            allocation_text = response.choices[0].message.content
            # Extract JSON from text (in case there's surrounding text)
            json_match = re.search(r'\{.*\}', allocation_text, re.DOTALL)
            if json_match:
                allocation_json = json.loads(json_match.group(0))
                return allocation_json
        except Exception as e:
            if os.getenv('DEBUG') == 'True':
                print(f"Error parsing budget JSON: {e}")
            # Fallback to simple text parsing if JSON extraction fails
            allocation = {}
            # Look for patterns like "Category Name: $X,XXX (XX%)"
            matches = re.findall(
                r'([A-Za-z\s]+):\s*\$?(\d,)+\.?\d*\s*\((\d+\.?\d*)%\)', text)
            for category, amount, percentage in matches:
                try:
                    amount_value = float(amount.replace(',', ''))
                    allocation[category.strip()] = {
                        "amount": amount_value,
                        "percentage": float(percentage)
                    }
                except ValueError:
                    continue

            # If we couldn't extract any allocations, create a simple one
            if not allocation:
                allocation = {"Total Budget": {
                    "amount": float(plan_amount), "percentage": 100.0}}

            return allocation


def main():
    # Load API key from environment variable
    api_key = os.getenv('PERPLEXITY_API_KEY')

    if not api_key:
        raise ValueError(
            "Please set the PERPLEXITY_API_KEY environment variable")

    # Initialize decoder
    decoder = NDISInvoiceDecoder(api_key)

    # Display welcome message
    print("===== Decode NDIS =====\n")
    print("This application helps NDIS participants and providers with:")
    print(" - Finding appropriate NDIS support codes")
    print(" - Understanding NDIS policies and guidelines")
    print(" - Recommending services based on needs")
    print(" - Staying updated with NDIS changes")
    print(" - Planning and allocating NDIS budgets\n")

    # Input loop
    while True:
        # Get user query
        query = input("How can we help you? (or 'q' to quit): ").strip()

        if query.lower() == 'q':
            print("Exiting application. Goodbye!")
            return

        if not query:
            print("Query cannot be empty. Please try again.")
            continue

        print(f"\nProcessing your query...")
        print("This may take a moment...")

        # Determine the type of query and route to appropriate feature
        result = None

        # Check if it's a policy question
        if any(keyword in query.lower() for keyword in ['can i', 'how do', 'what is', 'policy', 'rules', 'allowed', 'permitted']):
            print("Providing NDIS policy guidance...")
            result = decoder.get_ndis_policy_guidance(query)
            display_policy_results(result)

        # Check if it's a service recommendation request
        elif any(keyword in query.lower() for keyword in ['recommend', 'suggest', 'need help with', 'services for', 'supports for']):
            print("Recommending NDIS services...")
            result = decoder.recommend_services(query)
            display_recommendation_results(result)

        # Check if it's a budget planning request
        elif any(keyword in query.lower() for keyword in ['budget', 'allocate', 'funding', 'plan', 'money']):
            # Extract plan amount if mentioned
            import re
            amount_match = re.search(r'\$?(\d[\d,.]*)', query)
            plan_amount = 50000  # Default amount
            if amount_match:
                try:
                    plan_amount = float(amount_match.group(1).replace(',', ''))
                except ValueError:
                    pass

            print(f"Planning budget allocation for ${plan_amount:,.2f}...")
            result = decoder.plan_budget(plan_amount, query)
            display_budget_results(result)

        # Check if it's an updates request
        elif any(keyword in query.lower() for keyword in ['update', 'news', 'changes', 'recent', 'latest']):
            print("Fetching latest NDIS updates...")
            # Extract focus area if mentioned
            focus_area = None
            for area in ['pricing', 'eligibility', 'services', 'providers', 'participants']:
                if area in query.lower():
                    focus_area = area
                    break

            result = decoder.get_ndis_updates(focus_area)
            display_updates_results(result)

        # Default to code lookup for other queries
        else:
            print("Looking up NDIS codes...")
            result = decoder.decode_invoice(text_description=query)
            display_results(result)

        # Ask if user wants to ask another question
        another = input(
            "\nWould you like to ask another question? (y/n): ").strip().lower()
        if another != 'y':
            print("Exiting application. Goodbye!")
            return


def display_results(result):
    """Display the decoded NDIS results in a formatted way"""
    print("\n===== NDIS Code Lookup Results =====")

    # Display error if present
    if "error" in result and result["error"]:
        print(f"\nError: {result['error']}")
        return

    # Display codes
    print("\nDecoded NDIS Codes:")
    if result.get("codes"):
        for code in result.get("codes"):
            print(f"- {code}")
    else:
        print("No specific NDIS codes identified")

    # Display explanation
    print("\nExplanation:")
    print(result.get("explanation"))

    # Display citations
    print("\nCitations:")
    if result.get("citations"):
        for i, citation in enumerate(result.get("citations"), 1):
            print(f"{i}. {citation}")
    else:
        print("No citations provided")

    print("\n==============================")


def display_policy_results(result):
    """Display NDIS policy guidance results"""
    print("\n===== NDIS Policy Guidance =====")

    # Display error if present
    if "error" in result and result["error"]:
        print(f"\nError: {result['error']}")
        return

    # Display guidance
    print("\nGuidance:")
    guidance_text = result.get("guidance", "")
    # Format guidance for better readability
    for line in guidance_text.split('\n'):
        if line.startswith('##'):
            print(f"\n{line[2:].strip()}:")
        elif line.startswith('#'):
            print(f"\n{line[1:].strip()}")
        else:
            print(line)

    # Display related codes if any
    if result.get("related_codes"):
        print("\nRelated NDIS Codes:")
        for code in result.get("related_codes"):
            print(f"- {code['code']}: {code['name']}")

    # Display citations
    print("\nSources:")
    if result.get("citations"):
        for i, citation in enumerate(result.get("citations"), 1):
            print(f"{i}. {citation}")
    else:
        print("No sources cited")

    print("\n==============================")


def display_recommendation_results(result):
    """Display service recommendation results"""
    print("\n===== NDIS Service Recommendations =====")

    # Display error if present
    if "error" in result and result["error"]:
        print(f"\nError: {result['error']}")
        return

    # Display recommendation summary
    print("\nRecommended Services:")
    for service_type in result.get("service_types", []):
        print(f"- {service_type}")

    # Display detailed recommendation
    print("\nDetailed Recommendation:")
    recommendation_text = result.get("recommendation", "")
    for line in recommendation_text.split('\n'):
        print(line)

    # Display recommended codes
    if result.get("recommended_codes"):
        print("\nRecommended NDIS Codes:")
        # Limit to 5 codes for readability
        for code in result.get("recommended_codes")[:5]:
            print(f"- {code['code']}: {code['name']}")
        if len(result.get("recommended_codes", [])) > 5:
            print(
                f"  (and {len(result.get('recommended_codes')) - 5} more...)")

    print("\n==============================")


def display_updates_results(result):
    """Display NDIS updates results"""
    print("\n===== Latest NDIS Updates =====")

    # Display error if present
    if "error" in result and result["error"]:
        print(f"\nError: {result['error']}")
        return

    # Display last updated date
    if result.get("last_updated"):
        print(f"\nLast Updated: {result.get('last_updated')}")

    # Display key updates
    print("\nKey Updates:")
    for i, update in enumerate(result.get("key_updates", []), 1):
        print(f"\n{i}. {update.get('title', 'Update')}")
        if 'effective_date' in update:
            print(f"   Effective: {update['effective_date']}")
        if 'description' in update:
            print(f"   {update['description']}")

    # Display sources
    print("\nSources:")
    if result.get("sources"):
        for i, source in enumerate(result.get("sources"), 1):
            print(f"{i}. {source}")
    else:
        print("No sources cited")

    print("\n==============================")


def display_budget_results(result):
    """Display budget planning results"""
    print("\n===== NDIS Budget Planning =====")

    # Display error if present
    if "error" in result and result["error"]:
        print(f"\nError: {result['error']}")
        return

    # Display plan amount
    print(f"\nTotal Plan Amount: ${result.get('plan_amount', 0):,.2f}")

    # Display budget allocation
    print("\nRecommended Budget Allocation:")
    budget_allocation = result.get("budget_allocation", {})
    for category, details in budget_allocation.items():
        print(
            f"- {category}: ${details.get('amount', 0):,.2f} ({details.get('percentage', 0)}%)")

    # Display allocation summary
    print("\nAllocation Summary:")
    summary_text = result.get("allocation_summary", "")
    # Print just the first few lines for brevity
    lines = summary_text.split('\n')
    for line in lines[:10]:
        print(line)
    if len(lines) > 10:
        print("...")
        print("(Full details available in the detailed report)")

    # Display recommended codes
    if result.get("recommended_codes"):
        print("\nRecommended NDIS Codes:")
        for category, codes in result.get("recommended_codes", {}).items():
            if codes:
                print(f"\n{category}:")
                for code in codes[:2]:  # Limit to 2 codes per category for readability
                    print(f"- {code['code']}: {code['name']}")
                if len(codes) > 2:
                    print(f"  (and {len(codes) - 2} more...)")

    print("\n==============================")


if __name__ == "__main__":
    main()
