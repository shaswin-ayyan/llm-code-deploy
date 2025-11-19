import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

# Set a dummy API key before importing the app to avoid initialization errors
import os
os.environ['OPENAI_API_KEY'] = 'test_key_for_testing'

# Make sure the app path is correct
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_scraper():
    with patch('app.main.scraper', new_callable=MagicMock) as mock:
        mock.scrape_quiz_data = AsyncMock(return_value={
            "raw_html": "<html><body><h1>Quiz</h1><p>Question 1?</p></body></html>",
            "questions": ["Question 1?"],
            "submission_url": "/submit",
            "hidden_data": []
        })
        yield mock

@pytest.fixture
def mock_orchestrator():
    with patch('app.main.orchestrator', new_callable=MagicMock) as mock:
        mock.solve_question.return_value = "Answer 1"
        yield mock

@pytest.fixture
def mock_handler():
    with patch('app.main.handler', new_callable=MagicMock) as mock:
        mock.submit_answers.return_value = {"status": "success", "message": "Answers submitted"}
        yield mock

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "service": "Data Science Quiz Solver API"}

def test_solve_quiz_success(mock_scraper, mock_orchestrator, mock_handler):
    response = client.post(
        "/api/solve",
        json={"url": "http://example.com/quiz"}
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "submission_complete"
    assert "submission_details" in json_response
    mock_scraper.scrape_quiz_data.assert_called_once_with("http://example.com/quiz")
    mock_orchestrator.solve_question.assert_called_once()
    mock_handler.submit_answers.assert_called_once()

def test_solve_quiz_scraping_fails(mock_scraper):
    mock_scraper.scrape_quiz_data.side_effect = Exception("Scraping failed")
    response = client.post(
        "/api/solve",
        json={"url": "http://example.com/quiz"}
    )
    assert response.status_code == 500
    assert "An unexpected error occurred: Scraping failed" in response.json()["detail"]

def test_no_submission_url(mock_scraper, mock_orchestrator):
    # Create a new return value for the mock to avoid modifying the fixture for other tests
    new_return_value = {
        "raw_html": "<html><body><h1>Quiz</h1><p>Question 1?</p></body></html>",
        "questions": ["Question 1?"],
        "submission_url": None,
        "hidden_data": []
    }
    mock_scraper.scrape_quiz_data.return_value = new_return_value

    response = client.post(
        "/api/solve",
        json={"url": "http://example.com/quiz"}
    )
    assert response.status_code == 400
    assert "Submission URL not found" in response.json()["detail"]
