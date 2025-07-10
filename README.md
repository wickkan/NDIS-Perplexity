# Decode NDIS - Perplexity Hackathon

<a href="https://ndis-decoder-perplexity.windsurf.build" target="_blank">Decode NDIS App</a><br>
<a href="https://youtu.be/ciqQmZRncP4?si=YbowaFQ4sG-_YeHE" target="_blank">Decode NDIS Video Demo</a>

## Project Overview

Decode NDIS is a comprehensive AI-powered assistant designed specifically for NDIS (National Disability Insurance Scheme) participants, plan managers, and service providers in Australia. Our solution transforms how users navigate the complex NDIS ecosystem, leveraging Perplexity's Sonar API to provide accurate, real-time information.

## What is NDIS?

The National Disability Insurance Scheme (NDIS) is Australia’s publicly funded program that gives people with permanent and significant disability the resources to pursue their goals and live independently.

## Why We Built This

NDIS stakeholders face three persistent pain points:

1. Selecting the correct service code
2. Keeping up with policy changes
3. Planning and tracking budgets

Decode NDIS solves these problems through automation and real-time guidance.

### Key Features

#### 1. NDIS Code Interpretation

- Accurately extracts NDIS support item codes from service descriptions
- Uses a curated database of official NDIS codes for precision
- Provides clear explanations of code selection rationale
- Handles complex service descriptions with multiple potential codes

![gallery](https://github.com/user-attachments/assets/5e1ced9e-7fbb-4c97-8c33-2a2c02eb3762)

#### 2. Policy & Services Guidance

- Offers expert guidance on complex NDIS policies and rules
- Recommends appropriate NDIS services based on participant needs
- Considers participant details like age, location, and disability type
- Explains policy interpretations and appropriate service options
- Maps recommendations to specific NDIS support codes

![prompt2](https://github.com/user-attachments/assets/3da12317-8b4d-4a17-b68e-83934475c7d8)

#### 3. Real-time NDIS Updates

- Tracks and summarises the latest changes to NDIS policies and pricing
- Focuses on updates with significant impact on participants and providers
- Structures updates in an easy-to-understand format

![prompt4](https://github.com/user-attachments/assets/6726c17a-f75b-4590-8624-fca75843ce94)

#### 4. Budget Planning Assistant

- Helps allocate NDIS plan funding across support categories
- Considers participant needs, goals, and priorities
- Provides detailed breakdown with recommended services
- Links budget categories to relevant NDIS codes

![prompt3](https://github.com/user-attachments/assets/b71ab480-6c10-4ee7-9e57-0cf61050d5f4)

## How We Use Perplexity’s Sonar API

| Task            | Model                 |
| --------------- | --------------------- |
| Code lookup     | `sonar`               |
| Policy guidance | `sonar-reasoning`     |
| Live updates    | `sonar-pro`           |
| Budget planning | `sonar-reasoning-pro` |

Sonar supplies real-time data, sound reasoning and structured outputs that power each feature.

## Impact

• Cuts admin time by auto-coding invoices  
• Ensures every dollar is spent on eligible supports  
• Provides clear, up-to-date policy guidance  
• Keeps users compliant with the latest NDIS rules

## Hackathon Submission Category

This project is submitted in the category of **Health** as it addresses specific, documented challenges faced by NDIS participants and plan managers that are within the Australian healthcare system.

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
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Perplexity API key
cp .env.example .env
# Edit .env file to add your PERPLEXITY_API_KEY

# Run the Flask server
python app.py
```

The backend API will be available at http://localhost:3000

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
