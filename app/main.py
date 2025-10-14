from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests

from . import config
from . import generator
from . import github_utils
from . import evaluation_utils

app = FastAPI()

class Attachment(BaseModel):
    name: str
    url: str

class DeployRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: List[Attachment] = []

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/deploy")
async def deploy_app(request: DeployRequest):
    """
    Accepts a JSON POST request to build and deploy an application.
    """
    # 1. Check secret
    if request.secret != config.DEPLOYMENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    # 2. Generate app
    try:
        attachments_list = [att.model_dump() for att in request.attachments]
        generated_files = generator.generate_app(request.brief, attachments_list)
        print(f"Generated {len(generated_files)} files.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate application: {e}")

    # 3. Create repo, push files, and enable Pages
    repo_name = request.task
    try:
        repo_info = github_utils.create_repo(repo_name)
        repo_url = repo_info['response']['html_url']
        print(f"Repository created at: {repo_url}")

        commit_message = f"Initial commit for task: {request.task}"
        push_info = github_utils.push_files(repo_name, generated_files, commit_message)
        commit_sha = push_info['response']['commit_sha']
        print(f"Files pushed. Commit SHA: {commit_sha}")

        pages_info = github_utils.enable_pages(repo_name)
        pages_url = pages_info['response']['html_url']
        print(f"GitHub Pages enabled at: {pages_url}")
    except (requests.RequestException, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"GitHub operation failed: {e}")

    # 4. POST to evaluation.url
    try:
        evaluation_payload = {
            "email": request.email,
            "task": request.task,
            "round": request.round,
            "nonce": request.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        evaluation_utils.notify_evaluation(request.evaluation_url, evaluation_payload)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to notify evaluation server: {e}")

    # 5. Send final response
    return {
        "message": "Deployment and evaluation notification successful!",
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url,
    }
