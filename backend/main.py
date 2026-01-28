from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta, timezone

YOUTUBE_API_KEY = "AIzaSyAd1U97MMecg7oNfFUEp6EJH9Tzq-YPZC4I"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"

MIN_SUBSCRIBERS = 1_000_000

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# CACHE DIÁRIO
# =====================

CACHE = {
    "date": None,
    "hoje": [],
    "ontem": [],
    "semana": []
}

def canal_grande(channel_id):
    r = requests.get(CHANNELS_URL, params={
        "part": "statistics",
        "id": channel_id,
        "key": YOUTUBE_API_KEY
    })
    d = r.json()
    try:
        return int(d["items"][0]["statistics"]["subscriberCount"]) >= MIN_SUBSCRIBERS
    except:
        return False


def buscar(periodo_dias):
    published_after = (
        datetime.now(timezone.utc) - timedelta(days=periodo_dias)
    ).isoformat()

    r = requests.get(SEARCH_URL, params={
        "part": "snippet",
        "q": "official music video",
        "type": "video",
        "videoCategoryId": "10",
        "order": "date",
        "maxResults": 30,
        "publishedAfter": published_after,
        "key": YOUTUBE_API_KEY
    })

    data = r.json()
    artistas = {}

    for item in data.get("items", []):
        s = item["snippet"]
        channel_id = s["channelId"]

        if not canal_grande(channel_id):
            continue

        artista = s["channelTitle"]

        if artista not in artistas:
            artistas[artista] = {
                "artist": artista,
                "image": s["thumbnails"]["high"]["url"],
                "songs": []
            }

        artistas[artista]["songs"].append({
            "title": s["title"],
            "youtube": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        })

    return list(artistas.values())


def atualizar_cache():
    hoje = datetime.now().date().isoformat()

    if CACHE["date"] == hoje:
        return

    CACHE["date"] = hoje
    CACHE["hoje"] = buscar(1)
    CACHE["ontem"] = buscar(2)
    CACHE["semana"] = buscar(7)


@app.get("/period")
def period(period: str = "hoje"):
    atualizar_cache()
    return {
        "date": period,
        "artists": CACHE.get(period, [])
    }
