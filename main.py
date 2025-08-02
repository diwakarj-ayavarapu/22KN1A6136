from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime, timedelta
import random
import string
import logging
app = FastAPI(title="Simple URL Shortener")
# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shortener")
# In-memory URL store
short_links = {}
# Request model for creating short URLs
class URLCreateRequest(BaseModel):
    url: HttpUrl
    validity: Optional[int] = 30  # in minutes
    custom_code: Optional[str] = None
# Response model after URL is shortened
class URLCreateResponse(BaseModel):
    short_url: str
    expires_at: str
# Utility to generate a random shortcode
def create_random_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
# Utility to ensure unique shortcode
def get_unique_code(max_attempts: int = 5) -> str:
    for _ in range(max_attempts):
        code = create_random_code()
        if code not in short_links:
            return code
    raise HTTPException(status_code=500, detail="Unable to generate unique shortcode")
# Root endpoint
@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI URL Shortener. Use POST /shorten to create a short URL."}
# Create short URL endpoint
@app.post("/shorten", response_model=URLCreateResponse, status_code=201)
def shorten_url(payload: URLCreateRequest):
    code = payload.custom_code or get_unique_code()

    if code in short_links:
        logger.warning(f"Shortcode already in use: {code}")
        raise HTTPException(status_code=400, detail="Shortcode already exists")

    expiry = datetime.utcnow() + timedelta(minutes=payload.validity or 30)

    short_links[code] = {
        "original_url": str(payload.url),
        "expires_at": expiry
    }

    logger.info(f"New short URL created: /{code} → {payload.url} (expires at {expiry.isoformat()})")

    return URLCreateResponse(
        short_url=f"http://localhost:8000/{code}",
        expires_at=expiry.strftime("%Y-%m-%dT%H:%M:%SZ")
    )
# Redirect endpoint
@app.get("/{code}")
def redirect_to_original(code: str):
    link_info = short_links.get(code)

    if not link_info:
        logger.warning(f"Invalid shortcode requested: {code}")
        raise HTTPException(status_code=404, detail="Shortcode not found")

    if datetime.utcnow() > link_info["expires_at"]:
        logger.info(f"Shortcode expired and removed: {code}")
        del short_links[code]
        raise HTTPException(status_code=410, detail="Shortcode has expired")

    logger.info(f"Redirecting {code} → {link_info['original_url']}")
    return RedirectResponse(link_info["original_url"])
