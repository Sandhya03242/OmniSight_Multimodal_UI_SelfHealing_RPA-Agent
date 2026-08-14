from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright_bot import capture_homepage as run_checkout_flow


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


@app.post("/webhook/build")
def build_webhook(event: BuildEvent):

    if event.build_status.lower() != "success":

        return {
            "status": "ignored",
            "reason": "Build was not successful"
        }

    try:

        screenshots = run_checkout_flow(
            event.staging_url
        )

        return {
            "status": "success",
            "message": "Playwright workflow completed",
            "repository": event.repository,
            "branch": event.branch,
            "commit_sha": event.commit_sha,
            "screenshots": screenshots
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )