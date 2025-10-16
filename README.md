# LLM Code Deployment API

## 1. Project Overview

The **LLM Code Deployment API** is a sophisticated automation system designed to bridge the gap between AI-driven code generation and live deployment. It listens for API requests, generates complete web applications based on a provided brief, creates a GitHub repository, pushes the generated code, and activates GitHub Pages for immediate hosting. This platform is engineered for rapid, scalable, and reliable deployment of AI-generated applications, making it an ideal solution for hackathons, educational platforms, and rapid prototyping environments.

### Key Features:

- **Automated Code Generation**: Leverages AI (via AIPipe and `gpt-4.1-nano`) to generate `HTML`, `CSS`, and `JavaScript` code from a simple text brief.
- **End-to-End Deployment**: Automates the entire workflow from code creation to a live, publicly accessible URL.
- **GitHub Integration**: Seamlessly creates GitHub repositories, manages files, and enables GitHub Pages.
- **Scalable Architecture**: Built with `FastAPI` and designed to run in `Docker` containers, ensuring high performance and scalability.
- **Mock & Production Modes**: Includes a `MOCK_MODE` for safe local testing without making real API calls to external services.
- **Multi-Round Submissions**: Supports iterative development by allowing updates to an existing repository for subsequent rounds of a task.

---

## 2. System Architecture

The application is built on a modern Python stack and follows a modular, service-oriented architecture.

### Core Components:

- **FastAPI Application (`app/main.py`)**: The central API server that handles incoming deployment requests, orchestrates the workflow, and manages communication between components.
- **Code Generator (`app/generator.py`)**: Interfaces with the `AIPipe` service to generate application code. It constructs a detailed prompt, sends it to the AI model, and parses the response into a file structure.
- **GitHub Manager (`app/github_utils.py`)**: Manages all interactions with the GitHub API, including creating repositories, pushing files, and enabling GitHub Pages. It is designed to work in both production and mock modes.
- **Evaluation Notifier (`app/evaluation_utils.py`)**: Sends a notification to a specified callback URL upon successful deployment, providing key details like the repository URL and live pages URL.
- **Configuration (`app/config.py`)**: Loads all required credentials and settings from environment variables, ensuring that no sensitive information is hardcoded.

### Technology Stack:

- **Backend**: `Python 3.11`, `FastAPI`
- **Code Generation**: `AIPipe` (`gpt-4.1-nano`)
- **CI/CD & Hosting**: `GitHub`, `GitHub Actions`, `GitHub Pages`
- **Containerization**: `Docker`, `Docker Compose`
- **Dependencies**: `PyGithub`, `python-dotenv`, `requests`, `uvicorn`

---

## 3. Getting Started

Follow these steps to set up and run the application locally.

### Prerequisites:

- **Python 3.11**
- **Docker** and **Docker Compose**
- **Git**
- A **GitHub account** with a [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (`repo` and `workflow` scopes).
- An **AIPipe (OpenAI) API Key**.

### Local Setup Instructions:

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd llm-code-deployment-api
    ```

2.  **Configure Environment Variables**:
    Create a `.env` file in the `app/` directory by copying the example.
    ```bash
    cp app/.env.example app/.env
    ```
    Edit `app/.env` and fill in the required values:
    ```env
    # Deployment Security
    DEPLOYMENT_SECRET="your-strong-secret-key"

    # AI Service Configuration
    OPENAI_API_KEY="your-aipipe-or-openai-api-key"
    AIPIPE_EMAIL="your-aipipe-registered-email"

    # GitHub Configuration
    GITHUB_TOKEN="your-github-personal-access-token"
    GITHUB_USER="your-github-username"

    # Application Mode
    MOCK_MODE="True" # Set to "False" for production
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run with Docker Compose**:
    For a production-like setup, use Docker Compose.
    ```bash
    docker-compose up --build
    ```
    The API will be accessible at `http://localhost:8000`.

5.  **Run Locally for Debugging**:
    To run the app directly for easier debugging:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

---

## 4. Configuration

All configuration is managed via environment variables loaded by `app/config.py`.

| Variable            | Description                                                                                              | Default   |
| ------------------- | -------------------------------------------------------------------------------------------------------- | --------- |
| `DEPLOYMENT_SECRET` | A secret key to authorize deployment requests.                                                           | `None`    |
| `OPENAI_API_KEY`    | Your API key for the AIPipe/OpenAI service.                                                              | `None`    |
| `AIPIPE_EMAIL`      | The email associated with your AIPipe account.                                                           | `None`    |
| `GITHUB_TOKEN`      | Your GitHub Personal Access Token for API operations.                                                    | `None`    |
| `GITHUB_USER`       | Your GitHub username.                                                                                    | `None`    |
| `MOCK_MODE`         | If `True`, the app simulates API calls to GitHub and AIPipe. Set to `False` for live deployments.          | `True`    |
| `PORT`              | The port on which the FastAPI application runs.                                                          | `8000`    |

---

## 5. API Documentation

The API is fully documented using OpenAPI (Swagger) and ReDoc.

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

### Endpoints:

#### `GET /`

-   **Description**: Root endpoint to check service status.
-   **Response**: `{"status": "ready", "service": "LLM Code Deployment"}`

#### `GET /health`

-   **Description**: Provides a detailed health check of the API and its components.
-   **Response**:
    ```json
    {
      "status": "healthy",
      "service": "LLM Deployment API",
      "mode": "mock",
      "components": {
        "code_generator": true,
        "github_manager": true
      },
      "uptime": 120.5
    }
    ```

#### `POST /api/deploy`

-   **Description**: The main endpoint for generating and deploying a web application.
-   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "secret": "your-strong-secret-key",
      "task": "interactive-dashboard",
      "round": 1,
      "nonce": "unique-identifier-string",
      "brief": "Create a simple dashboard with a chart and a data table.",
      "checks": ["check1", "check2"],
      "evaluation_url": "https://eval-service.example.com/notify",
      "attachments": [
        {
          "name": "data.csv",
          "url": "data:text/csv;base64,..."
        }
      ]
    }
    ```
-   **Success Response (200 OK)**:
    ```json
    {
      "status": "success",
      "message": "Round 1 deployment completed",
      "repo_url": "https://github.com/your-user/interactive-dashboard",
      "commit_sha": "mock_commit_sha",
      "pages_url": "https://your-user.github.io/interactive-dashboard/",
      "generated_files": ["index.html", "README.md", "LICENSE"],
      "mode": "mock",
      "action": "created"
    }
    ```
-   **Error Responses**:
    -   `403 Forbidden`: Invalid `DEPLOYMENT_SECRET`.
    -   `500 Internal Server Error`: An error occurred during code generation or GitHub operations.

---

## 6. Deployment

The application is designed to be deployed using Docker.

1.  **Build the Docker Image**:
    ```bash
    docker build -t llm-deployer .
    ```

2.  **Run the Container**:
    ```bash
    docker run -d -p 8000:8000 \
      --name llm-deployer-instance \
      -e DEPLOYMENT_SECRET="your-production-secret" \
      -e OPENAI_API_KEY="your-production-aipipe-key" \
      -e AIPIPE_EMAIL="your-production-email" \
      -e GITHUB_TOKEN="your-production-github-token" \
      -e GITHUB_USER="your-github-username" \
      -e MOCK_MODE="False" \
      llm-deployer
    ```

For a more robust setup, consider using a managed container service like **AWS Fargate**, **Google Cloud Run**, or **Azure Container Apps**.

---

## 7. Testing

The project includes a suite of tests to ensure reliability.

### Running Tests:

To run the full test suite, use `pytest`:

```bash
python -m pytest
```

The tests are located in the `tests/` directory and use FastAPI's `TestClient` to simulate API requests in a controlled environment. The tests are configured to run in `MOCK_MODE` to avoid making real API calls.

---

## 8. License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.