from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import time
from .generator import CodeGenerator
print("🚀 Starting LLM Code Deployment API...")
start_time = time.time()

# Import config first
from . import config
print(f"✅ Config loaded in {time.time() - start_time:.2f}s")

app = FastAPI(title="LLM Code Deployment API")

# Initialize components with error handling
try:
    from .generator import CodeGenerator
    code_generator = CodeGenerator()
    print(f"✅ CodeGenerator initialized in {time.time() - start_time:.2f}s")
except Exception as e:
    print(f"❌ CodeGenerator initialization failed: {e}")
    code_generator = None

try:
    from .github_utils import github_manager
    print(f"✅ GitHub manager initialized in {time.time() - start_time:.2f}s")
except Exception as e:
    print(f"❌ GitHub manager initialization failed: {e}")
    github_manager = None

try:
    from .evaluation_utils import notify_evaluation_service
    print(f"✅ Evaluation utils loaded in {time.time() - start_time:.2f}s")
except Exception as e:
    print(f"❌ Evaluation utils failed: {e}")
    # Create a mock function
    def notify_evaluation_service(url, data):
        print(f"📨 Mock evaluation notification to: {url}")
        return True

print(f"🎉 App fully loaded in {time.time() - start_time:.2f} seconds")

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
    return {"status": "ready", "service": "LLM Code Deployment"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "LLM Deployment API",
        "mode": "mock" if config.MOCK_MODE else "production",
        "components": {
            "code_generator": code_generator is not None,
            "github_manager": github_manager is not None
        },
        "uptime": time.time() - start_time
    }

@app.post("/api/deploy")
async def deploy_app(request: DeployRequest):
    """
    Main deployment endpoint for both Round 1 and Round 2
    """
    print(f"🎯 Received deployment request for: {request.email} (Round {request.round})")
    
    # 1. Verify secret
    if request.secret != config.DEPLOYMENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid deployment secret")
    
    # 2. Generate application code
    try:
        print(f"📝 Generating app for: {request.email}")
        attachments_data = [att.dict() for att in request.attachments]
        
        if code_generator:
            generated_files = code_generator.generate_app(request.brief, attachments_data)
        else:
            generated_files = {
                "index.html": f"<html><body><h1>Fallback App</h1><p>{request.brief}</p></body></html>",
                "README.md": f"# Fallback App\n\n{request.brief}",
                "LICENSE": "MIT License"
            }
            
        print(f"✅ Generated {len(generated_files)} files")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")
    
    # 3. GitHub operations - CRITICAL FIX: Use SAME repo for all rounds
    # Always use the base task name without round suffix for the repository
    repo_name = request.task  # Use just the task name, no round suffix
    
    try:
        if request.round == 1:
            # ROUND 1: Create new repository
            print(f"🔧 Creating NEW repository: {repo_name}")
            repo_info = github_manager.create_repo(repo_name)
            repo_url = repo_info['response']['html_url']
            
            commit_message = f"Round {request.round}: {request.brief[:50]}..."
            push_info = github_manager.push_files(repo_name, generated_files, commit_message)
            commit_sha = push_info['response']['commit_sha']
            
        else:
            # ROUND 2+: Update existing repository (SAME repo as Round 1)
            print(f"🔧 Updating EXISTING repository: {repo_name}")
            
            # Get repo info (this will work for existing repos)
            repo_info = github_manager.create_repo(repo_name)  # This now handles existing repos
            repo_url = repo_info['response']['html_url']
            
            commit_message = f"Round {request.round} Update: {request.brief[:50]}..."
            push_info = github_manager.update_repo(repo_name, generated_files, commit_message)
            commit_sha = push_info['response']['commit_sha']
        
        # Enable/update Pages (same for both rounds)
        pages_info = github_manager.enable_pages(repo_name)
        pages_url = pages_info['response']['html_url']
        
        print(f"✅ GitHub operations completed for {repo_name}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub operations failed: {str(e)}")
    
    # 4. Evaluation service notification
    try:
        print(f"📨 Sending evaluation notification to: {request.evaluation_url}")
        
        evaluation_data = {
            "email": request.email,
            "task": request.task,
            "round": request.round,
            "nonce": request.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        
        success = notify_evaluation_service(request.evaluation_url, evaluation_data)
        if not success:
            print("⚠️ Evaluation service notification failed, but continuing...")
            
    except Exception as e:
        print(f"⚠️ Evaluation notification failed: {e}")
    
    # 5. Return success response
    return {
        "status": "success",
        "message": f"Round {request.round} deployment completed",
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url,
        "generated_files": list(generated_files.keys()),
        "mode": "mock" if config.MOCK_MODE else "production",
        "action": "updated" if request.round > 1 else "created"
    }