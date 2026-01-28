from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta, timezone

# =====================
# CONFIGURAÇÃO
# =====================

YOUTUBE_API_KEY = "AIzaSyAd1U97MMecg7oNfFUEp6EJH9Tzq-YPZC4"

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
# FUNÇÕES
# =====================

def get_channel_subscribers(channel_id: str) -> int:
    params = {
        "part": "statistics",
        "id": channel_id,
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(CHANNELS_URL, params=params)
    data = response.json()

    try:
        return int(data["items"][0]["statistics"]["subscriberCount"])
    except:
        return 0


def buscar_lancamentos(dias: int):
    published_after = (
        datetime.now(timezone.utc) - timedelta(days=dias)
    ).isoformat()

    params = {
        "part": "snippet",
        "q": "official music video",
        "type": "video",
        "videoCategoryId": "10",
        "order": "date",
        "maxResults": 20,
        "publishedAfter": published_after,
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(SEARCH_URL, params=params)
    data = response.json()

    resultados = []

    for item in data.get("items", []):
        snippet = item["snippet"]
        channel_id = snippet["channelId"]

        inscritos = get_channel_subscribers(channel_id)

        if inscritos < MIN_SUBSCRIBERS:
            continue  # ignora canal pequeno

        resultados.append({
            "artist": snippet["channelTitle"],
            "title": snippet["title"],
            "image": snippet["thumbnails"]["high"]["url"],
            "youtube": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "spotify": None,
            "subscribers": inscritos
        })

    return resultados


# =====================
# ROTAS
# =====================

@app.get("/")
def home():
    return {"status": "Na Música Hoje - backend online"}

@app.get("/period")
def period(period: str = "hoje"):
    if period == "hoje":
        dias = 1
        label = "Hoje"
    elif period == "ontem":
        dias = 2
        label = "Ontem"
    else:
        dias = 7
        label = "Na Semana"

    itens = buscar_lancamentos(dias)

    return {
        "date": label,
        "items": itens
    }
