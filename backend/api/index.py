from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from the parent directory
from app import app as flask_app

# Configure CORS for the serverless environment
CORS(flask_app, resources={r"/api/*": {"origins": "*"}})

# Netlify function handler
def handler(event, context):
    # Get the path and HTTP method from the event
    path = event.get('path', '')
    http_method = event.get('httpMethod', '')
    
    # Create a request context
    with flask_app.test_request_context(
        path=path,
        method=http_method,
        headers=event.get('headers', {}),
        data=event.get('body', '')
    ):
        # Process the request
        try:
            response = flask_app.full_dispatch_request()
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': str(e)
            }
