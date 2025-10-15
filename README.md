# Smart Task Planner

The Smart Task Planner is a web application that helps you break down a large goal into a manageable, dependency-aware task plan. Just provide your goal and an optional deadline, and the application will generate a clear, actionable plan for you.

## Features

*   **Goal-oriented Planning:** Simply state your goal, and the AI will generate a detailed task plan.
*   **Dependency-aware:** The generated plan identifies dependencies between tasks, so you know what to work on first.
*   **Timeline Generation:** Each task comes with a suggested timeline to help you stay on track.
*   **Simple and Intuitive UI:** A clean and user-friendly interface for a seamless experience.

## Tech Stack

*   **Frontend:** React, TypeScript, Vite, Bootstrap
*   **Backend:** Python, FastAPI
*   **AI:** Google Gemini

## Demo Video

* https://drive.google.com/drive/folders/18vI12yqTu3nesoVTfyjzjbyVbUtH9Mwf?usp=sharing

## Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

*   Node.js and npm (for the frontend)
*   Python 3.7+ and pip (for the backend)
*   A Google Gemini API key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Smart-Task-Planner.git
    cd Smart-Task-Planner
    ```

2.  **Set up the backend:**
    *   Navigate to the `backend` directory:
        ```bash
        cd backend
        ```
    *   Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
        ```
    *   Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```
    *   Create a `.env` file and add your Gemini API key:
        ```
        GEMINI_API_KEY=your_api_key
        ```

3.  **Set up the frontend:**
    *   Navigate to the `frontend` directory:
        ```bash
        cd ../frontend
        ```
    *   Install the required npm packages:
        ```bash
        npm install
        ```

### Running the Application

1.  **Start the backend server:**
    *   In the `backend` directory, run:
        ```bash
        uvicorn api:app --reload --port 8000
        ```

2.  **Start the frontend development server:**
    *   In the `frontend` directory, run:
        ```bash
        npm run dev
        ```

The application should now be running at `http://localhost:5173`.

## Project Structure

```
Smart-Task-Planner/
├── backend/
│   ├── api.py          # FastAPI application
│   └── gemini_api.py   # Gemini API client
├── frontend/
│   ├── src/
│   │   ├── App.tsx     # Main React component
│   │   └── ...
│   └── ...
└── README.md
```

## API Endpoints

*   **`POST /generate-plan`**: Generates a task plan based on a goal and an optional deadline.
    *   **Request Body:**
        ```json
        {
          "goal": "Your goal here",
          "deadline": "Optional deadline"
        }
        ```
    *   **Response:**
        ```json
        [
          {
            "id": 1,
            "name": "Task 1",
            "timeline": "Day 1-2",
            "dependencies": []
          },
          ...
        ]
        ```
