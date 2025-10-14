# LLM Code Deployment Automator

This project is a FastAPI application that automates the building and deployment of simple web applications based on a given brief. It's designed to handle requests, generate code (currently mocked), create a GitHub repository, push the code, enable GitHub Pages, and notify an evaluation server.

## Project Structure

```
.
├── app/
│   ├── main.py               # Main FastAPI application and API endpoint
│   ├── config.py             # Configuration loader (reads .env)
│   ├── generator.py          # Mock application generator
│   ├── github_utils.py       # Handles GitHub API interactions
│   ├── evaluation_utils.py   # Handles notifications to the evaluation server
│   └── .env                  # Environment variables (secret, mock_mode)
├── requirements.txt          # Project dependencies
├── README.md                 # This file
└── LICENSE                   # Project license
```

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd llm-code-deployment
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a file named `.env` inside the `app/` directory. This file holds the deployment secret.

    ```ini
    # app/.env
    DEPLOYMENT_SECRET="my-super-secret"
    ```

## Running the Application

Once set up, you can run the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application will be running at `http://localhost:8000`.

## Usage

The primary endpoint is `/api/deploy`. You can send a POST request to it with a JSON payload that matches the project's specification.

### Mock Mode

This application includes a `MOCK_MODE` flag (set to `True` by default in `config.py`) that simulates external API calls to GitHub and the evaluation server. When enabled, the application will print the actions it would take to the console instead of making real network requests. This is useful for testing the application flow without needing a GitHub token or a live evaluation endpoint.

To run in "real" mode, you would set `MOCK_MODE=False` in your environment and configure `app/github_utils.py` with a valid GitHub Personal Access Token.

### Example Request

You can use `curl` to test the endpoint:

```bash
curl -X POST http://localhost:8000/api/deploy \
-H "Content-Type: application/json" \
-d '{
  "email": "student@example.com",
  "secret": "my-super-secret",
  "task": "sum-of-sales-abcde",
  "round": 1,
  "nonce": "ab12-...",
  "brief": "Create a sum-of-sales page.",
  "checks": [],
  "evaluation_url": "https://example.com/notify",
  "attachments": [{
    "name": "data.csv",
    "url": "data:text/csv;base64,cHJvZHVjdCxzYWxlcwpBcHBsZSwxMC41MEIKQmFuYW5hLDUuMDAKQ2hlcnJ5LDE1LjI1Cg=="
  }]
}'
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
