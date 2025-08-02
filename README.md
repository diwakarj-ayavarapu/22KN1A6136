# URL Shortener Microservice

## Overview
This microservice provides URL shortening functionality with a RESTful API built using FastAPI.

## Requirements
- Python 3.7+
- FastAPI
- Uvicorn
- Pydantic

## Installation
1. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Service
Start the server with:
```
uvicorn main:app --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Create Short URL
- **POST** `/shorturls`
- Request body:
  ```json
  {
    "url": "https://example.com",
    "validity": 30,
    "shortcode": "customcode"  // optional
  }
  ```
- Response:
  ```json
  {
    "shortLink": "http://localhost:8000/customcode",
    "expiry": "2025-01-01T00:30:00Z"
  }
  ```

### Redirect Short URL
- **GET** `/{shortcode}`
- Redirects to the original URL if valid and not expired.

## Design Document
See `DESIGN.md` for architectural and design details.

## Notes
- The service uses an in-memory store; data will be lost on restart.
- For production, consider using persistent storage and additional features like authentication.
