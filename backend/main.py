from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permite o site conversar com o backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/releases")
def releases():
    return {
        "date": "Hoje",
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
