from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from urllib.parse import urljoin
import asyncio
from .scraper.scraper import WebScraper
from .ai_orchestrator.orchestrator import AIOrchestrator
from .submission_handler.handler import SubmissionHandler
from . import config

app = FastAPI(title="Data Science Quiz Solver API")

class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str

scraper = WebScraper()
orchestrator = AIOrchestrator()
handler = SubmissionHandler()

async def run_solve_quiz_chain(initial_request: QuizRequest):
    """
    Asynchronous wrapper to run the quiz solving chain.
    """
    await solve_quiz_chain(initial_request)

async def solve_quiz_chain(initial_request: QuizRequest):
    """
    This function will be run in the background.
    It will handle the entire quiz-solving chain.
    """
    current_url = initial_request.url
    email = initial_request.email
    secret = initial_request.secret
    
    while current_url:
        print(f"--- Solving Quiz at: {current_url} ---")
        try:
            # Step 1: Scrape the website
            scraped_data = await scraper.scrape_quiz_data(current_url)
            
            # Step 2: Use the AI orchestrator to get the answer
            # The orchestrator will be enhanced to handle complex logic later
            answer_payload = orchestrator.construct_answer_payload(scraped_data, email, secret, current_url)
            
            # Step 3: Submit the answer
            submission_url = scraped_data.get("submission_url")
            if not submission_url:
                print("❌ Submission URL not found. Ending chain.")
                break

            full_submission_url = urljoin(current_url, submission_url)
            submission_response = handler.submit_answers(full_submission_url, answer_payload)
            
            # Step 4: Check for a new URL in the response
            if submission_response and "url" in submission_response:
                new_url = submission_response.get("url")
                if new_url and new_url != current_url:
                    print(f"✅ Correct answer! Proceeding to next quiz: {new_url}")
                    current_url = new_url
                else:
                    print("🏁 Quiz chain finished or no new URL provided.")
                    current_url = None
            else:
                print("❌ Submission failed or response did not contain a new URL. Ending chain.")
                current_url = None

        except Exception as e:
            print(f"❌ An error occurred in the quiz chain: {e}")
            current_url = None
            
    print("--- Quiz chain complete. ---")

@app.get("/")
def read_root():
    return {"status": "ready", "service": "Data Science Quiz Solver API"}

@app.post("/api/solve")
async def solve_quiz(request: QuizRequest, background_tasks: BackgroundTasks):
    """
    Receives a quiz URL, verifies the secret, and starts the solving process in the background.
    """
    if request.secret != config.QUIZ_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret.")
    
    background_tasks.add_task(run_solve_quiz_chain, request)
    
    return {"status": "accepted", "message": "Quiz solving process has been started."}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
