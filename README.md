# Decode NDIS - Perplexity Hackathon

<a href="https://ndis-decoder-perplexity.windsurf.build" target="_blank">Decode NDIS App</a><br>
<a href="https://youtu.be/ciqQmZRncP4?si=YbowaFQ4sG-_YeHE" target="_blank">Decode NDIS Video Demo</a>

## Project Overview

Decode NDIS is a comprehensive AI-powered assistant designed specifically for NDIS (National Disability Insurance Scheme) participants, plan managers, and service providers in Australia. Our solution transforms how users navigate the complex NDIS ecosystem, leveraging Perplexity's Sonar API to provide accurate, real-time information.

## What is NDIS?

The National Disability Insurance Scheme (NDIS) is an Australian government program that provides individualised funding and support to people with significant and permanent disabilities. Unlike many systems in the US, the NDIS:

- Gives eligible participants direct control over their support plans and funding
- Allows participants to choose services and providers that best suit their personal goals and needs
- Is publicly funded, not means-tested, and operates independently from other social welfare systems
- Focuses specifically on disability-related supports (personal care, assistive technology, therapy, etc.)
- Currently supports over 717,000 Australians with disabilities

Despite its benefits, NDIS participants face significant challenges navigating the system's complex codes, policies, and budgeting requirements. Decode NDIS addresses these pain points directly.

## Why We Built This

As of 2025, the NDIS allocates an average of **$82,500 per participant annually**, but actual spending averages just **$66,200** — meaning critical supports are going unused. With **63% of participants using plan managers**, there’s clear demand for tools that simplify navigation, ensure compliance, and maximise outcomes.

New laws from **October 2024** now restrict funding to **approved services only**, and the government has launched an **$83.9M crackdown on fraud**, increasing the stakes for correct invoicing and policy adherence.

Our team identified three critical challenges faced by NDIS participants and plan managers:

1. **Complex Coding System**: NDIS uses an intricate coding system for all billable services that is difficult to navigate
2. **Constantly Changing Policies**: NDIS guidelines frequently change, making it hard to stay informed
3. **Budget Management Complexity**: Participants struggle to optimise their funding allocations across different support categories

These challenges often result in denied claims, underspent budgets, and participants missing out on entitled supports.

### Key Features

#### 1. NDIS Code Interpretation

- Accurately extracts NDIS support item codes from service descriptions
- Uses a curated database of official NDIS codes for precision
- Provides clear explanations of code selection rationale
- Handles complex service descriptions with multiple potential codes

#### 2. Policy & Services Guidance

- Offers expert guidance on complex NDIS policies and rules
- Recommends appropriate NDIS services based on participant needs
- Considers participant details like age, location, and disability type
- Explains policy interpretations and appropriate service options
- Maps recommendations to specific NDIS support codes

#### 3. Real-time NDIS Updates

- Tracks and summarises the latest changes to NDIS policies and pricing
- Focuses on updates with significant impact on participants and providers
- Structures updates in an easy-to-understand format

#### 4. Budget Planning Assistant

- Helps allocate NDIS plan funding across support categories
- Considers participant needs, goals, and priorities
- Provides detailed breakdown with recommended services
- Links budget categories to relevant NDIS codes

## How We Leveraged Perplexity's Sonar API

This project showcases the power of Perplexity's Sonar API through:

1. **Model-Specific Optimisation**: We carefully selected the optimal Sonar model for each feature:

   - `sonar` for factual code lookup queries requiring precision
   - `sonar-reasoning` for policy guidance and service recommendations needing thoughtful analysis
   - `sonar-pro` for real-time NDIS updates requiring current internet-sourced information
   - `sonar-reasoning-pro` for complex budget planning requiring in-depth chain-of-thought reasoning

2. **Real-Time Information Access**: Sonar's internet-enabled search capabilities provide the most current NDIS policy updates and pricing guides, critical for a system that frequently changes.

3. **Chain-of-Thought Reasoning**: For complex queries like budget planning, we leverage Sonar's reasoning capabilities to show users the step-by-step logic behind recommendations.

4. **Response Formatting**: We refined the API response handling to convert natural language outputs into structured, user-friendly formats.

## Impact for Users

Decode NDIS transforms how participants interact with the NDIS by:

1. **Reducing Administrative Burden**: Automating complex coding tasks that previously required expert knowledge
2. **Increasing Access to Support**: Helping participants discover and utilise all entitled services
3. **Optimising Funding Usage**: Preventing underspent budgets through intelligent allocation recommendations
4. **Enhancing Decision-Making**: Providing clear policy guidance for informed choices
5. **Future-Proofing**: Ensuring users always have access to the latest NDIS information and updates

## Hackathon Submission Category

This project is submitted in the category of **Health** as it addresses specific, documented challenges faced by NDIS participants and plan managers that are within the Australian healthcare system.

## Technology Stack

## Demo Prompts Used

During our demo video, we showcase Decode NDIS using the following real-world queries:

1. **Code Interpretation**  
   _"What is the NDIS code for House or Yard Maintenance?"_

2. **Policy & Services Guidance**  
   _"Can I use NDIS funds for food delivery or sports activities?"_

3. **NDIS Updates**  
   _"What’s changed in NDIS funding or rules in 2025?"_

4. **Budget Planning**  
   _"Help me split $20,000 across Core, Capacity Building, and Capital Supports"_

### Backend

- **Python Flask API**: Provides RESTful endpoints for all features with CORS support
- **Perplexity Sonar API**: Powers the intelligent reasoning with specialised models tailored for each feature
- **NDIS Support Catalogue**: Curated database of official NDIS codes and pricing

### Frontend

- **Next.js & React**: Component-based UI for intuitive user experience
- **Responsive Design**: Works on desktop and mobile devices
- **Accessible Interface**: Designed with NDIS participants' needs in mind

## Project Structure

Our codebase is organised into backend and frontend components:

### Backend

- `backend/` - Python Flask API with Perplexity Sonar integration
  - `main.py` - Core implementation of all NDIS decoder features with Perplexity Sonar API
  - `app.py` - Flask API endpoints with CORS support for frontend integration
  - `data/` - NDIS support catalogue and reference data
  - `utils/` - Helper utilities
  - `requirements.txt` - Python dependencies

### Frontend

- `frontend/` - Next.js React frontend
  - `src/app/` - Next.js app router pages
  - `src/components/` - React components including:
    - `invoice-chat.tsx` - Main chat interface component
    - `results.tsx` - Results display for all NDIS features
    - `invoice-upload.tsx` - File upload functionality
    - `ui/` - Reusable UI components
  - `src/lib/` - Utility functions and API client

## API Endpoints

### Code Interpretation

- `POST /api/decode` - Decode service descriptions into NDIS codes

### Policy & Services Guidance

- `POST /api/policy-guidance` - Get expert guidance on NDIS policies and service recommendations

### NDIS Updates

- `GET /api/ndis-updates` - Get the latest NDIS policy updates and news

### Budget Planning

- `POST /api/plan-budget` - Get budget allocation recommendations

### System Status

- `GET /api/health` - Check API health and available features

## Getting Started

### Prerequisites

- Python 3.8+ for the backend
- Node.js 16+ for the frontend
- Perplexity API key

### Setup Instructions

#### Backend

```bash
# From the project root
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Perplexity API key
cp .env.example .env
# Edit .env file to add your PERPLEXITY_API_KEY

# Run the Flask server
python app.py
```

The backend API will be available at http://localhost:3001

#### Frontend

```bash
# From the project root
cd frontend

# Install dependencies
pnpm install  # or npm install

# Create .env file
cp .env.example .env

# Start the development server
pnpm dev  # or npm run dev
```

The frontend development server will be available at http://localhost:3000
