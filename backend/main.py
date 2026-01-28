from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DADOS MOCKADOS (substitui depois por YouTube/Spotify reais)
DATA = {
    "Jorge e Mateus": {
        "photo": "https://i.pravatar.cc/150?img=12",
        "releases": {
            0: ["Solidão Desenfreada"],
            1: [],
            7: ["Solidão Desenfreada"]
        }
    },
    "Rihanna": {
        "photo": "https://i.pravatar.cc/150?img=47",
        "releases": {
            0: ["New Song"],
            1: [],
            7: ["New Song"]
        }
    },
    "Lady Gaga": {
        "photo": "https://i.pravatar.cc/150?img=32",
        "releases": {
            0: [],
            1: ["Yesterday Song"],
            7: ["Yesterday Song"]
        }
    }
}

@app.get("/period")
def get_period(period: str = "hoje"):
    if period == "hoje":
        days = 0
    elif period == "ontem":
        days = 1
    else:
        days = 7

    target_date = date.today() - timedelta(days=days)

    artists = []

    for artist, data in DATA.items():
        songs = data["releases"].get(days, [])
        if songs:
            artists.append({
                "name": artist,
                "photo": data["photo"],
                "songs": songs
            })

    return {
        "date": target_date.strftime("%d/%m"),
        "artists": artists
    }
