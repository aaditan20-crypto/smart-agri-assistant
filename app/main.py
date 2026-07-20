from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.orchestrator import orchestrator
from app.models.schemas import FarmerInput
from app.utils.token_tracker import get_total_tokens_used

app = FastAPI(title="Smart Agriculture Assistant")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("app/static/index.html")

@app.post("/plan")
def get_farming_plan(farmer_input: FarmerInput):
    result = orchestrator.run(farmer_input)
    return result

@app.get("/monitoring/tokens")
def token_usage_summary():
    return get_total_tokens_used()