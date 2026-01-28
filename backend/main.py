from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta, timezone

# =====================
# CONFIGURAÇÃO ÚNICA
# =====================

YOUTUBE_API_KEY = "AIzaSyAd1U97MMecg7oNfFUEp6EJH9Tzq-YPZC4"

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
# FUNÇÃO PRINCIPAL
# =====================

def buscar_lancamentos(dias: int):
    """
    Busca lançamentos musicais recentes no YouTube
    (últimas 24h, 48h ou 7 dias)
    """

    published_after = (
        datetime.now(timezone.utc) - timedelta(days=dias)
    ).isoformat()

    params = {
        "part": "snippet",
        "q": "official music video",
        "type": "video",
        "videoCategoryId": "10",
        "order": "date",
        "maxResults": 15,
        "publishedAfter": published_after,
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = response.json()

    resultados = []

    for item in data.get("items", []):
        snippet = item["snippet"]

        resultados.append({
            "artist": snippet["channelTitle"],
            "title": snippet["title"],
            "image": snippet["thumbnails"]["high"]["url"],
            "youtube": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "spotify": None
        })

    return resultados


# =====================
# ROTAS DA API
# =====================

@app.get("/")
def home():
    return {"status": "Na Música Hoje - backend online"}

@app.get("/period")
def period(period: str = "hoje"):
    """
    period:
    - hoje
    - ontem
    - semana
    """

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
