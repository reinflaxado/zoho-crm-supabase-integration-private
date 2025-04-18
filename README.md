# Zoho CRM to Supabase Integration

A Python-based webhook receiver that connects Zoho CRM to a Supabase database.

## Features
- FastAPI webhook server to receive Zoho CRM notifications
- Zoho API integration for data synchronization
- Supabase client for database operations
- Deployment ready for Render, Fly.io, or Railway

## Setup
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (see `.env.example`)
4. Run the server: `uvicorn app.main:app --reload`

## Project Structure
```
├── app/                  # Application code
│   ├── api/              # API endpoints
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration
│   └── main.py           # Entry point
├── tests/                # Test files
├── .env                  # Environment variables (git-ignored)
├── .env.example          # Example environment variables
├── requirements.txt      # Project dependencies
├── Dockerfile            # For containerization
└── README.md             # This file
``` 