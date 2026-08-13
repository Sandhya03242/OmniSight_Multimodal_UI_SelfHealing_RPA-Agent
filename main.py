from fastapi import FastAPI, HTTPException
from pydantic import BaseM


app = FastAPI(
    title="OmniSight",
    description="Multimodal UI Self-Healing & RPA Agent",
    version="0.1.0"
)
class BuildEvent(BaseModel):
    repository: str
    branch: str
    commit_sha: str
    staging_url: str
    build_status: str


@app.get("/")
def root():

    return {
        "project": "OmniSight",
        "status": "running"
    }