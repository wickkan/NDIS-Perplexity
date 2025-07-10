"""
Test script for NDIS Decoder backend
Tests all enhanced API endpoints and verifies citation functionality
"""
import requests
import json
import time
from pprint import pprint

BASE_URL = "http://127.0.0.1:9000/api"

# Configure session with appropriate headers
session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "http://127.0.0.1:3000"  # Simulate request from frontend
})

# Global variable to store session ID for context tests
session_cookie = None

def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    
    response = session.get(f"{BASE_URL}/health")
    print(f"Status code: {response.status_code}")
    print("Response:")
    pprint(response.json())
    
    return response.status_code == 200

def test_code_lookup(description="Assistance with self-care activities", region="VIC"):
    """Test code lookup endpoint"""
    print_section("Testing Code Lookup Endpoint")
    
    payload = {
        "description": description,
        "region": region
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    response = session.post(f"{BASE_URL}/decode", json=payload)
    
    print(f"Status code: {response.status_code}")
    result = response.json()
    
    # Print key parts of the response
    print("\nResponse highlights:")
    print(f"Confidence: {result.get('confidence_indicator', 'Not provided')}")
    print(f"Summary: {result.get('summary', 'Not provided')}")
    print(f"Verification: {result.get('verification_status', 'Not provided')}")
    
    # Check for citations
    print("\nCitations:")
    citations = result.get('citations', [])
    if citations:
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation.get('url', 'No URL')} - {citation.get('source', 'Unknown source')}")
    else:
        print("No citations found in response")
    
    # Save full response to file for inspection
    with open("code_lookup_response.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nFull response saved to code_lookup_response.json")
    
    return response.status_code == 200

def test_policy_guidance(query="What are the rules for SIL funding?", category="Housing"):
    """Test policy guidance endpoint"""
    print_section("Testing Policy Guidance Endpoint")
    
    payload = {
        "query": query,
        "category": category
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    response = session.post(f"{BASE_URL}/policy-guidance", json=payload)
    
    print(f"Status code: {response.status_code}")
    result = response.json()
    
    # Print key parts of the response
    print("\nResponse highlights:")
    print(f"Confidence: {result.get('confidence_indicator', 'Not provided')}")
    print(f"Summary: {result.get('summary', 'Not provided')}")
    print(f"Verification: {result.get('verification_status', 'Not provided')}")
    
    # Check for citations
    print("\nCitations:")
    citations = result.get('citations', [])
    if citations:
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation.get('url', 'No URL')} - {citation.get('source', 'Unknown source')}")
    else:
        print("No citations found in response")
    
    # Save full response to file for inspection
    with open("policy_guidance_response.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nFull response saved to policy_guidance_response.json")
    
    return response.status_code == 200

def test_service_recommendations():
    """Test service recommendations endpoint"""
    print_section("Testing Service Recommendations Endpoint")
    
    payload = {
        "needs_description": "I need help with daily activities and mobility",
        "participant_details": {
            "age": 35,
            "disability": "physical",
            "region": "NSW"
        }
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    response = session.post(f"{BASE_URL}/recommend-services", json=payload)
    
    print(f"Status code: {response.status_code}")
    result = response.json()
    
    # Print key parts of the response
    print("\nResponse highlights:")
    print(f"Confidence: {result.get('confidence_indicator', 'Not provided')}")
    print(f"Summary: {result.get('summary', 'Not provided')}")
    print(f"Verification: {result.get('verification_status', 'Not provided')}")
    
    # Check for citations
    print("\nCitations:")
    citations = result.get('citations', [])
    if citations:
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation.get('url', 'No URL')} - {citation.get('source', 'Unknown source')}")
    else:
        print("No citations found in response")
    
    # Save full response to file for inspection
    with open("service_recommendations_response.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nFull response saved to service_recommendations_response.json")
    
    return response.status_code == 200

def test_ndis_updates():
    """Test NDIS updates endpoint"""
    print_section("Testing NDIS Updates Endpoint")
    
    params = {
        "focus": "pricing",
        "period": "6 months",
        "region": "QLD"
    }
    
    print(f"Request params: {json.dumps(params, indent=2)}")
    response = session.get(f"{BASE_URL}/ndis-updates", params=params)
    
    print(f"Status code: {response.status_code}")
    result = response.json()
    
    # Print key parts of the response
    print("\nResponse highlights:")
    print(f"Confidence: {result.get('confidence_indicator', 'Not provided')}")
    print(f"Summary: {result.get('summary', 'Not provided')}")
    print(f"Verification: {result.get('verification_status', 'Not provided')}")
    
    # Check for citations
    print("\nCitations:")
    citations = result.get('citations', [])
    if citations:
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation.get('url', 'No URL')} - {citation.get('source', 'Unknown source')}")
    else:
        print("No citations found in response")
    
    # Save full response to file for inspection
    with open("ndis_updates_response.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nFull response saved to ndis_updates_response.json")
    
    return response.status_code == 200

def test_budget_planning():
    """Test budget planning endpoint"""
    print_section("Testing Budget Planning Endpoint")
    
    payload = {
        "plan_amount": 50000,
        "needs_description": "I need assistance with daily activities and therapy",
        "existing_supports": ["Personal care"],
        "priorities": ["Therapy", "Transport"],
        "region": "ACT"
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    response = session.post(f"{BASE_URL}/plan-budget", json=payload)
    
    print(f"Status code: {response.status_code}")
    result = response.json()
    
    # Print key parts of the response
    print("\nResponse highlights:")
    print(f"Confidence: {result.get('confidence_indicator', 'Not provided')}")
    print(f"Summary: {result.get('summary', 'Not provided')}")
    print(f"Verification: {result.get('verification_status', 'Not provided')}")
    
    # Check for citations
    print("\nCitations:")
    citations = result.get('citations', [])
    if citations:
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation.get('url', 'No URL')} - {citation.get('source', 'Unknown source')}")
    else:
        print("No citations found in response")
    
    # Save full response to file for inspection
    with open("budget_planning_response.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nFull response saved to budget_planning_response.json")
    
    return response.status_code == 200

def test_context_preservation():
    """Test context preservation across multiple queries"""
    print_section("Testing Context Preservation")
    
    # Clear any existing session cookies to start fresh
    session.cookies.clear()
    
    # First query to establish context
    print("\n1. Making initial query about personal care...")
    payload1 = {"description": "Personal care assistance", "region": "VIC"}
    response1 = session.post(f"{BASE_URL}/decode", json=payload1)
    print(f"Status code: {response1.status_code}")
    
    # Show session cookies from this response
    print(f"Session cookies: {session.cookies.get_dict()}")
    
    time.sleep(1)  # Brief pause
    
    # Second query that should use context from first - using same session with cookies
    print("\n2. Making follow-up query referring to previous context...")
    payload2 = {"query": "What are the rules for this support?", "category": "Daily Living"}
    response2 = session.post(f"{BASE_URL}/policy-guidance", json=payload2)
    print(f"Status code: {response2.status_code}")
    result2 = response2.json()
    
    # Check context endpoint - using same session with cookies
    print("\n3. Checking stored context...")
    response3 = session.get(f"{BASE_URL}/context")
    print(f"Status code: {response3.status_code}")
    
    if response3.status_code == 200:
        context = response3.json()
        print("\nStored context:")
        pprint(context)
        return True
    else:
        print(f"Error getting context: {response3.text}")
    return False

def test_pin_item():
    """Test pinning an item for future reference"""
    print_section("Testing Pin Item Functionality")
    
    # Clear any existing session cookies to start fresh
    session.cookies.clear()
    
    # First make a request to establish session
    init_response = session.get(f"{BASE_URL}/health")
    if init_response.status_code != 200:
        print("Failed to initialize session")
        
    print(f"Session cookies after health check: {session.cookies.get_dict()}")
    
    # Item to pin
    payload = {
        "item": {
            "type": "support_code",
            "code": "01_011_0107_1_1",
            "description": "Assistance with Self-Care Activities - Standard - Weekday Daytime",
            "note": "Important code for daily support"
        }
    }
    
    print("Request payload:", json.dumps(payload, indent=2))
    response = session.post(f"{BASE_URL}/pin-item", json=payload)
    print(f"Status code: {response.status_code}")
    
    try:
        print("Response:", response.json())
    except Exception as e:
        print(f"No valid JSON response: {str(e)}")
    
    # Verify the item was pinned by checking context
    context_response = session.get(f"{BASE_URL}/context")
    print(f"Context status code: {context_response.status_code}")
    
    if context_response.status_code == 200:
        try:
            context = context_response.json()
            print("Context content:")
            pprint(context)
            
            pinned_items = context.get('context', {}).get('pinned_items', [])
            if pinned_items:
                print("\nSuccessfully verified item was pinned in context")
                return True
        except Exception as e:
            print(f"Error parsing context: {str(e)}")
    
    return response.status_code == 200 and context_response.status_code == 200

def run_all_tests():
    """Run all tests and summarize results"""
    print_section("NDIS Decoder Backend Test Suite")
    
    tests = [
        ("Health Check", test_health),
        ("Code Lookup", test_code_lookup),
        ("Policy Guidance", test_policy_guidance),
        ("Service Recommendations", test_service_recommendations),
        ("NDIS Updates", test_ndis_updates),
        ("Budget Planning", test_budget_planning),
        ("Context Preservation", test_context_preservation),
        ("Pin Item", test_pin_item)
    ]
    
    results = {}
    
    for name, test_func in tests:
        print(f"\nRunning test: {name}")
        try:
            success = test_func()
            results[name] = "PASS" if success else "FAIL"
        except Exception as e:
            print(f"Error during test: {str(e)}")
            results[name] = "ERROR"
    
    print_section("Test Results Summary")
    for name, result in results.items():
        print(f"{name.ljust(25)}: {result}")

if __name__ == "__main__":
    run_all_tests()
