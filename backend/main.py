from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Na Música Hoje está no ar 🎵"}
