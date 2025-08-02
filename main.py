from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime, timedelta
import random
import string
import logging
import uvicorn
app = FastAPI()
@app.get("/")
def root():
    return {"message": "Welcome to the URL Shortener API. Use POST /shorturls to create short URLs."}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("url-shortener")
logger.setLevel(logging.INFO)
url_store = {}
class ShortenURLRequest(BaseModel):
    url: HttpUrl
    validity: Optional[int] = 30  
    shortcode: Optional[str] = None
class ShortenURLResponse(BaseModel):
    shortLink: str
    expiry: str
def generate_shortcode(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
def get_unique_shortcode(retries=5):
    for _ in range(retries):
        code = generate_shortcode()
        if code not in url_store:
            return code
    raise HTTPException(status_code=500, detail="Could not generate unique shortcode, please try again")
@app.post("/shorturls", response_model=ShortenURLResponse, status_code=201)
def create_short_url(request: ShortenURLRequest):
    if request.shortcode:
        code = request.shortcode
        if code in url_store:
            logger.warning(f"Attempt to create duplicate shortcode: {code}")
            raise HTTPException(status_code=400, detail="Shortcode already exists")
    else:
        code = get_unique_shortcode()

    expiry_time = datetime.utcnow() + timedelta(minutes=request.validity or 30)

    url_store[code] = {
        "original_url": str(request.url),
        "expiry": expiry_time
    }

    logger.info(f"Created shortcode {code} for URL {request.url} with expiry {expiry_time.isoformat()}")

    return ShortenURLResponse(
        shortLink=f"http://localhost:8000/{code}",
        expiry=expiry_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    )

@app.get("/{shortcode}")
def redirect_short_url(shortcode: str):
    entry = url_store.get(shortcode)
    if not entry:
        logger.warning(f"Shortcode not found: {shortcode}")
        raise HTTPException(status_code=404, detail="Shortcode not found")

    if datetime.utcnow() > entry["expiry"]:
        logger.info(f"Shortcode expired: {shortcode}")
        del url_store[shortcode]
        raise HTTPException(status_code=410, detail="Shortcode expired")

    logger.info(f"Redirecting shortcode {shortcode} to {entry['original_url']}")
    return RedirectResponse(entry["original_url"])
