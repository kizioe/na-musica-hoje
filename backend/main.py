from fastapi import FastAPI
import requests
import datetime
import os

app = FastAPI()

YOUTUBE_API_KEY = os.getenv("AIzaSyAd1U97MMecg7oNfFUEp6EJH9Tzq-YPZC4")

MIN_SUBSCRIBERS = 500_000
CACHE = {}

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"


def today():
    return datetime.date.today().isoformat()


def fetch_youtube_results(query, published_after):
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoCategoryId": "10",
        "publishedAfter": published_after,
        "maxResults": 25,
        "key": YOUTUBE_API_KEY,
    }

    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=20)
    return r.json().get("items", [])


def get_channel_info(channel_id):
    params = {
        "part": "statistics,snippet",
        "id": channel_id,
        "key": YOUTUBE_API_KEY,
    }

    r = requests.get(YOUTUBE_CHANNELS_URL, params=params, timeout=20)
    items = r.json().get("items", [])

    if not items:
        return None

    data = items[0]

    return {
        "subs": int(data["statistics"].get("subscriberCount", 0)),
        "verified": data["snippet"].get("customUrl") is not None,
        "image": data["snippet"]["thumbnails"]["high"]["url"],
    }


def iso_days_ago(days):
    d = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    return d.isoformat("T") + "Z"


def build_data(days):
    key = f"{today()}_{days}"

    if key in CACHE:
        return CACHE[key]

    queries = [
        "new song",
        "new single",
        "new music video",
        "official audio",
        "lançamento música",
        "nova música",
    ]

    artists = {}

    published_after = iso_days_ago(days)

    for q in queries:
        results = fetch_youtube_results(q, published_after)

        for item in results:
            snippet = item["snippet"]

            channel_id = snippet["channelId"]
            channel_title = snippet["channelTitle"]

            info = get_channel_info(channel_id)

            if not info:
                continue

            if info["subs"] < MIN_SUBSCRIBERS and not info["verified"]:
                continue

            title = snippet["title"]

            if "cover" in title.lower():
                continue

            if channel_title not in artists:
                artists[channel_title] = {
                    "artist": channel_title,
                    "image": info["image"],
                    "subs": info["subs"],
                    "songs": [],
                }

            artists[channel_title]["songs"].append({
                "title": title,
                "youtube": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            })

    result = list(artists.values())

    result.sort(key=lambda x: x["subs"], reverse=True)

    CACHE[key] = result

    return result


@app.get("/period")
def get_period(period: str = "hoje"):

    if period == "hoje":
        days = 1
    elif period == "ontem":
        days = 2
    elif period == "semana":
        days = 7
    else:
        days = 1

    data = build_data(days)

    return {
        "date": period,
        "artists": data
    }
