import os
import traceback

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from main import NDISInvoiceDecoder

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for frontend requests
allowed_origins = os.getenv(
    'ALLOWED_ORIGINS', 'http://localhost:3000,https://ndis-decoder-perplexity.windsurf.build/').split(',')
# CORS Configuration
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "https://ndis-decoder-perplexity.windsurf.build",
                "http://localhost:3000"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 600,
        }
    }
)

# Add CORS headers to all responses


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin',
                         'https://ndis-decoder-perplexity.windsurf.build')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


# Get API key
api_key = os.getenv('PERPLEXITY_API_KEY')
if not api_key:
    raise ValueError("Please set the PERPLEXITY_API_KEY environment variable")

# Initialize decoder
decoder = NDISInvoiceDecoder(api_key)


@app.before_request
def handle_options():
    if request.method.lower() == 'options':
        return Response()


@app.route('/api/decode', methods=['POST', 'OPTIONS'])
def decode_description():
    """
    API endpoint to decode NDIS service descriptions
    """
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'No description provided'}), 400

    try:
        result = decoder.decode_invoice(text_description=query)
        return jsonify(result)
    except Exception as e:
        if os.getenv('DEBUG') == 'True':
            traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/policy-guidance', methods=['POST', 'OPTIONS'])
def get_policy_guidance():
    """
    API endpoint to get NDIS policy guidance
    """
    data = request.json
    query = data.get('query', '')
    category = data.get('category', None)

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        result = decoder.get_ndis_policy_guidance(query, category)
        return jsonify(result)
    except Exception as e:
        if os.getenv('DEBUG') == 'True':
            traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend-services', methods=['POST', 'OPTIONS'])
def recommend_services():
    """
    API endpoint to recommend NDIS services based on needs
    """
    data = request.json
    query = data.get('query', '')
    participant_details = data.get('participant_details', {})

    if not query:
        return jsonify({'error': 'No needs description provided'}), 400

    try:
        result = decoder.recommend_services(
            needs_description=query, participant_details=participant_details)
        return jsonify(result)
    except Exception as e:
        if os.getenv('DEBUG') == 'True':
            traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/ndis-updates', methods=['POST', 'OPTIONS'])
def get_ndis_updates():
    """
    API endpoint to get latest NDIS updates and news
    """
    query = request.args.get('query', None)
    time_period = request.args.get('period', "3 months")

    try:
        result = decoder.get_ndis_updates(
            focus_area=query, time_period=time_period)
        return jsonify(result)
    except Exception as e:
        if os.getenv('DEBUG') == 'True':
            traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/plan-budget', methods=['POST', 'OPTIONS'])
def plan_budget():
    """
    API endpoint to help allocate NDIS plan budget
    """
    data = request.json
    plan_amount = float(data.get('plan_amount', 0))
    needs_description = data.get('needs_description', '')
    existing_supports = data.get('existing_supports', [])
    priorities = data.get('priorities', [])

    if plan_amount <= 0:
        return jsonify({'error': 'Invalid plan amount'}), 400
    if not needs_description:
        return jsonify({'error': 'No needs description provided'}), 400

    try:
        result = decoder.plan_budget(
            plan_amount, needs_description, existing_supports, priorities)
        return jsonify(result)
    except Exception as e:
        if os.getenv('DEBUG') == 'True':
            traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return jsonify({
        'status': 'healthy',
        'service': 'NDIS Decoder API',
        'features': [
            'Code Lookup',
            'Policy Guidance',
            'Service Recommendations',
            'NDIS Updates',
            'Budget Planning'
        ]
    })


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
