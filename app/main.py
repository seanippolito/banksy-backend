from fastapi import FastAPI

app = FastAPI(title="Banksy Backend")

@app.on_event("startup")
async def show_startup_message():
    print("Banksy Backend available at http://127.0.0.1:8000 (mapped from 0.0.0.0 inside Docker), health check is available at http://127.0.0.1:8000/api/v1/health")

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "service": "Banksy Backend Test Me ✅"}
