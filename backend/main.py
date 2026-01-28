from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": "NaMusicaHoje/1.0 (contato@email.com)"
}

def get_artist_image(artist_name):
    search = requests.get(
        "https://musicbrainz.org/ws/2/artist/",
        params={
            "query": artist_name,
            "fmt": "json",
            "limit": 1
        },
        headers=HEADERS
    ).json()

    if not search.get("artists"):
        return None

    artist_id = search["artists"][0]["id"]

    image = f"https://coverartarchive.org/artist/{artist_id}/front-250"
    return image

@app.get("/period")
def get_period(period: str = "hoje"):
    if period == "hoje":
        days = 0
    elif period == "ontem":
        days = 1
    else:
        days = 7

    target_date = date.today() - timedelta(days=days)

    # EXEMPLO REAL (depois você amplia)
    raw_data = {
        "Rihanna": ["Lift Me Up"],
        "Lady Gaga": ["Bloody Mary"],
        "Taylor Swift": ["Cruel Summer"]
    }

    artists = []

    for artist, songs in raw_data.items():
        photo = get_artist_image(artist)
        artists.append({
            "name": artist,
            "photo": photo,
            "songs": songs
        })

    return {
        "date": target_date.strftime("%d/%m"),
        "artists": artists
    }
