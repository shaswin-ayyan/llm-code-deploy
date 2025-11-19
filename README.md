# Data Science Quiz Solver API

## 1. Project Overview

The **Data Science Quiz Solver API** is an automated system designed to solve data science quizzes found on web pages. The application receives a URL to a quiz, scrapes the content, uses a large language model (LLM) to analyze the questions and generate answers, and then submits the answers to the quiz's submission endpoint.

### Key Features:

- **Automated Web Scraping**: Uses `Playwright` to scrape quiz content, even from dynamic, JavaScript-heavy websites.
- **AI-Powered Quiz Solving**: Leverages an LLM (`gpt-4.1-nano`) to analyze the quiz structure and solve the questions.
- **Efficient Token Usage**: A multi-step AI process first analyzes the quiz structure and then solves each question individually, which is more efficient than sending the entire quiz in a single request.
- **Automated Answer Submission**: The system automatically submits the AI-generated answers to the quiz's submission URL.
- **Modular Architecture**: The application is built with a clean, modular design, with separate components for scraping, AI orchestration, and submission.

---

## 2. System Architecture

The application is built on a modern Python stack and follows a modular, service-oriented architecture.

### System Design Diagram

```
+-----------------+      +---------------------+      +----------------------+
|                 |      |                     |      |                      |
|  FastAPI Server |----->|    Web Scraper      |----->|   Quiz Website       |
|  (app/main.py)  |      | (Playwright)        |      | (External)           |
|                 |      |                     |      |                      |
+-------+---------+      +---------------------+      +----------------------+
        |
        |
        v
+-----------------+      +----------------------+
|                 |      |                      |
| AI Orchestrator |----->|   LLM                |
| (gpt-4.1-nano)  |      | (AIPipe/OpenRouter)  |
|                 |      |                      |
+-------+---------+      +----------------------+
        |
        |
        v
+-----------------+      +----------------------+
|                 |      |                      |
| Submission      |----->|   Submission URL     |
| Handler         |      | (External)           |
|                 |      |                      |
+-----------------+      +----------------------+
```

### Core Components:

- **FastAPI Application (`app/main.py`)**: The main API server that receives the quiz URL and orchestrates the entire workflow.
- **Web Scraper (`app/scraper/scraper.py`)**: Uses `Playwright` to scrape the quiz's HTML content.
- **AI Orchestrator (`app/ai_orchestrator/orchestrator.py`)**: Manages all interactions with the LLM, including analyzing the quiz structure and solving the questions.
- **Submission Handler (`app/submission_handler/handler.py`)**: Submits the AI-generated answers to the quiz's submission URL.

### Technology Stack:

- **Backend**: `Python 3.11`, `FastAPI`
- **Web Scraping**: `Playwright`, `BeautifulSoup4`
- **AI Model**: `gpt-4.1-nano` (via AIPipe or OpenRouter)
- **Testing**: `pytest`, `unittest.mock`

---

## 3. Getting Started

Follow these steps to set up and run the application locally.

### Prerequisites:

- **Python 3.11**
- **Git**
- An **API key** for your chosen LLM provider (e.g., AIPipe, OpenRouter).

### Local Setup Instructions:

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd data-science-quiz-solver
    ```

2.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your LLM API key:
    ```env
    OPENAI_API_KEY="your-llm-api-key"
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright Browsers**:
    ```bash
    playwright install
    ```

5.  **Run the Application**:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    The API will be accessible at `http://localhost:8000`.

---

## 4. API Documentation

The API is fully documented using OpenAPI (Swagger).

-   **Swagger UI**: `http://localhost:8000/docs`

### Endpoints:

#### `POST /api/solve`

-   **Description**: The main endpoint for solving a data science quiz.
-   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "secret": "your_quiz_secret",
      "url": "http://www.example.com/quiz-843"
    }
    ```
-   **Success Response (200 OK)**:
    ```json
    {
      "status": "submission_complete",
      "url": "http://www.example.com/quiz-843",
      "submission_details": {
        "status": "success",
        "status_code": 200,
        "response_body": "..."
      }
    }
    ```
-   **Error Responses**:
    -   `404 Not Found`: The quiz URL could not be reached.
    -   `500 Internal Server Error`: An error occurred during the solving process.

---

## 5. Testing

The project includes a suite of tests to ensure reliability.

### Running Tests:

To run the full test suite, use `pytest`:

```bash
python -m pytest
```

The tests are located in the `tests/` directory and use FastAPI's `TestClient` to simulate API requests and mock external services.
