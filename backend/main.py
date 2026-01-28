from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta, timezone
import os

# =====================
# CONFIG
# =====================

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") or "AIzaSyAd1U97MMecg7oNfFUEp6EJH9Tzq-YPZC4"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# HELPERS
# =====================

def search_youtube(period_days: int):
    """
    Busca músicas lançadas recentemente no YouTube
    """
    published_after = (
        datetime.now(timezone.utc) - timedelta(days=period_days)
    ).isoformat()

    params = {
        "part": "snippet",
        "q": "official music video",
        "type": "video",
        "videoCategoryId": "10",  # Music
        "maxResults": 15,
        "order": "date",
        "publishedAfter": published_after,
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = response.json()

    results = []

    for item in data.get("items", []):
        snippet = item["snippet"]

        title = snippet["title"]
        channel = snippet["channelTitle"]
        thumbnails = snippet["thumbnails"]
        video_id = item["id"]["videoId"]

        results.append({
            "artist": channel,
            "title": title,
            "image": thumbnails["high"]["url"],
            "youtube": f"https://www.youtube.com/watch?v={video_id}",
            "spotify": None  # depois a gente integra
        })

    return results


# =====================
# ROUTES
# =====================

@app.get("/")
def home():
    return {"status": "Na Música Hoje - backend online"}

@app.get("/period")
def get_period(period: str = "hoje"):
    """
    period:
    - hoje
    - ontem
    - semana
    """

    if period == "hoje":
        days = 1
        label = "Hoje"
    elif period == "ontem":
        days = 2
        label = "Ontem"
    else:
        days = 7
        label = "Na Semana"

    items = search_youtube(days)

    return {
        "date": label,
        "items": items
    }
