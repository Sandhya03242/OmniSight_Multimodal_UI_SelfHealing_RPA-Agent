from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="OmniSight",
    description="Multimodal UI Self-Healing & RPA Agent",
    version="1.0.0"
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


@app.post("/build-event")
def build_event(event: BuildEvent):
    return {
        "message": "Build event received",
        "repository": event.repository,
        "branch": event.branch,
        "commit_sha": event.commit_sha,
        "staging_url": event.staging_url,
        "build_status": event.build_status
    }