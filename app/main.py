from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urljoin
from .scraper.scraper import WebScraper
from .ai_orchestrator.orchestrator import AIOrchestrator
from .submission_handler.handler import SubmissionHandler

app = FastAPI(title="Data Science Quiz Solver API")

class QuizRequest(BaseModel):
    url: str

scraper = WebScraper()
orchestrator = AIOrchestrator()
handler = SubmissionHandler()

@app.get("/")
def read_root():
    return {"status": "ready", "service": "Data Science Quiz Solver API"}

@app.post("/api/solve")
async def solve_quiz(request: QuizRequest):
    """
    The complete end-to-end quiz solving pipeline.
    """
    print(f"Received quiz URL: {request.url}")
    try:
        # Step 1: Scrape the website
        scraped_data = await scraper.scrape_quiz_data(request.url)
        html_content = scraped_data.get("raw_html", "")
        if not html_content:
            raise HTTPException(status_code=404, detail="Could not retrieve content from URL.")

        # The new scraper provides the questions and submission URL directly
        questions_text = scraped_data.get("questions", [])
        submission_url = scraped_data.get("submission_url")

        # Combine visible questions with any hidden data found
        context_for_solving = "\n".join(questions_text) + "\n" + "\n".join(scraped_data.get("hidden_data", []))
        
        answers = {}
        for i, question_str in enumerate(questions_text):
            answer = orchestrator.solve_question(question_str, context_for_solving)
            answers[f"question_{i+1}"] = answer
        
        # Step 4: Submit the answers
        if not submission_url:
            raise HTTPException(status_code=400, detail="Submission URL not found in quiz structure.")
        
        # Ensure the submission URL is absolute
        full_submission_url = urljoin(request.url, submission_url)
        
        submission_result = handler.submit_answers(full_submission_url, answers)

        return {
            "status": "submission_complete",
            "url": request.url,
            "submission_details": submission_result
        }

    except Exception as e:
        print(f"An error occurred during the process: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
