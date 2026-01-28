from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 COLE SUA API KEY AQUI
YOUTUBE_API_KEY = "AIzaSyAd1U97MMecg7oNfFUEp6EJH9Tzq-YPZC4"

CACHE = {}

def search_new_music(hours):
    today_key = datetime.utcnow().strftime("%Y-%m-%d")
    cache_key = f"{today_key}_{hours}"

    if cache_key in CACHE:
        return CACHE[cache_key]

    published_after = (
        datetime.utcnow() - timedelta(hours=hours)
    ).isoformat("T") + "Z"

    params = {
        "part": "snippet",
        "type": "video",
        "videoCategoryId": "10",
        "publishedAfter": published_after,
        "maxResults": 30,
        "key": YOUTUBE_API_KEY
    }

    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params=params,
        timeout=10
    )
    data = r.json()

    artists = {}

    for item in data.get("items", []):
        channel = item["snippet"]["channelTitle"]

        # 🎯 só canais oficiais de música
        if not channel.endswith(" - Topic"):
            continue

        artist = channel.replace(" - Topic", "").strip()
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]

        if artist not in artists:
            artists[artist] = {
                "name": artist,
                "photo": None,  # agora assumimos fallback
                "songs": []
            }

        artists[artist]["songs"].append({
            "title": title,
            "youtube": f"https://www.youtube.com/watch?v={video_id}"
        })

    result = list(artists.values())
    CACHE[cache_key] = result
    return result

@app.get("/period")
def get_period(period: str = "hoje"):
    if period == "hoje":
        hours = 24
    elif period == "ontem":
        hours = 48
    else:
        hours = 168  # 7 dias

    date_label = datetime.now().strftime("%d/%m")

    artists = search_new_music(hours)

    return {
        "date": date_label,
        "artists": artists
    }
