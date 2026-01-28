from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 COLE SUA API KEY DO YOUTUBE AQUI
YOUTUBE_API_KEY = "COLE_SUA_API_KEY_AQUI"

HEADERS = {
    "User-Agent": "NaMusicaHoje/1.0 (contato@email.com)"
}

# 🧠 CACHE EM MEMÓRIA (zera a cada deploy / dia)
CACHE = {}

def clean_artist_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"( - topic|vevo|official|oficial|channel)", "", name)
    name = re.sub(r"\(.*?\)", "", name)
    return name.strip().title()

def get_artist_image(artist_name):
    variations = [
        artist_name,
        clean_artist_name(artist_name)
    ]

    for name in variations:
        try:
            r = requests.get(
                "https://musicbrainz.org/ws/2/artist/",
                params={
                    "query": name,
                    "fmt": "json",
                    "limit": 1
                },
                headers=HEADERS,
                timeout=10
            )
            data = r.json()
            if data.get("artists"):
                artist_id = data["artists"][0]["id"]
                return f"https://coverartarchive.org/artist/{artist_id}/front-250"
        except:
            continue

    return None

def search_youtube_music(days):
    today_key = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"{today_key}_{days}"

    if cache_key in CACHE:
        return CACHE[cache_key]

    published_after = (
        datetime.utcnow() - timedelta(days=days)
    ).isoformat("T") + "Z"

    params = {
        "part": "snippet",
        "q": "official audio OR official video",
        "type": "video",
        "videoCategoryId": "10",
        "publishedAfter": published_after,
        "maxResults": 20,
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

        artist_raw = channel.replace(" - Topic", "").strip()
        artist = clean_artist_name(artist_raw)

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

    result = list(artists.values())
    CACHE[cache_key] = result
    return result

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
