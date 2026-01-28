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

# 🔐 COLE SUA API KEY DO YOUTUBE AQUI
YOUTUBE_API_KEY = "AIzaSyAd1U97MMecg7oNfFUEp6EJH9Tzq-YPZC4"

HEADERS = {
    "User-Agent": "NaMusicaHoje/1.0 (contato@email.com)"
}

def get_artist_image(artist_name):
    try:
        r = requests.get(
            "https://musicbrainz.org/ws/2/artist/",
            params={
                "query": artist_name,
                "fmt": "json",
                "limit": 1
            },
            headers=HEADERS,
            timeout=10
        )
        data = r.json()
        if not data.get("artists"):
            return None
        artist_id = data["artists"][0]["id"]
        return f"https://coverartarchive.org/artist/{artist_id}/front-250"
    except:
        return None

def search_youtube_music(days):
    published_after = (
        datetime.utcnow() - timedelta(days=days)
    ).isoformat("T") + "Z"

    params = {
        "part": "snippet",
        "q": "official audio OR official video",
        "type": "video",
        "videoCategoryId": "10",
        "publishedAfter": published_after,
        "maxResults": 15,
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
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        video_id = item["id"]["videoId"]

        # Heurística simples: artista = nome do canal
        artist = channel.replace(" - Topic", "").strip()

        if artist not in artists:
            artists[artist] = {
                "name": artist,
                "photo": get_artist_image(artist),
                "songs": []
            }

        artists[artist]["songs"].append({
            "title": title,
            "youtube": f"https://www.youtube.com/watch?v={video_id}"
        })

    return list(artists.values())

@app.get("/period")
def get_period(period: str = "hoje"):
    if period == "hoje":
        days = 0
    elif period == "ontem":
        days = 1
    else:
        days = 7

    date_label = (datetime.now() - timedelta(days=days)).strftime("%d/%m")

    artists = search_youtube_music(days)

    return {
        "date": date_label,
        "artists": artists
    }
