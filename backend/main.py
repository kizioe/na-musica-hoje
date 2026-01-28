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

@app.get("/releases")
def releases(days: int = 0):
    target_date = date.today() - timedelta(days=days)

    return {
        "date": target_date.strftime("%d/%m"),
        "items": [
            {
                "artist": "Lana Del Rey",
                "title": "Ocean Blvd",
                "spotify": "https://www.spotify.com",
                "youtube": "https://www.youtube.com"
            },
            {
                "artist": "BK'",
                "title": "Novo Amor",
                "spotify": "https://www.spotify.com",
                "youtube": None
            }
        ]
    }
