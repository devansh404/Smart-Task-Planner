from google import genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json

def generate_plan_from_llm(goal: str, deadline: str) -> dict:
    """
    Generates a task plan by calling the Gemini LLM.
    """

    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client()
    
    prompt = f"""
    You are an expert project manager. Analyze the following user goal and break it down into a series of simple actionable tasks.

    **Goal:** "{goal}"
    **Deadline:** "{deadline}"

    **Instructions:**
    1. Divide the goal into manageable tasks.
    2. For each task, provide a concise description.
    3. Calculate a realistic timeline for each task based on the goal's total duration. The final task's timeline should not exceed the goal's deadline.
    4. Return the output as a single valid JSON object with a key "plan", which contains a list of task objects. Each task object must include: "id" (integer), "task" (string), "description" (string), and "deadline" (string in HH hours/DD days format).
    Following is the example JSON format for each task object:
    [
        {
        "id": 1,
        "name": "Define MVP & acceptance criteria",
        "description": "Write concise scope and success metrics for the launch.",
        "timeline": "4 hours"
        },
        {
        "id": 2,
        "name": "Wireframes & user flow",
        "description": "Design the basic layout and flow of user screens.",
        "timeline": "6 hours"
        },
        {
        "id": 3,
        "name": "Backend APIs & database schema",
        "description": "Implement core API endpoints and schema for products and users.",
        "timeline": "2 days"
        }
    ]
    Do not wrap the JSON in markdown code fences.
    """
    try:
        response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt
        )
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    
    except Exception as e:
        print(f"Error processing LLM response: {e}")
        return {"error": "Failed to generate or parse the plan."}

app = FastAPI(title="Task Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GoalRequest(BaseModel):
    goal: str
    deadline: str

# --- API Endpoint ---
@app.post("/generate-plan")
async def create_plan(request: GoalRequest):
    """
    Accepts a user goal and returns a structured task plan.
    """
    plan = generate_plan_from_llm(request.goal, request.deadline)
    if "error" in plan:
        raise HTTPException(status_code=500, detail=plan["error"])
    return plan

# To run this app:
# 1. pip install fastapi uvicorn google-generativeai python-dotenv
# 2. Set your GOOGLE_API_KEY environment variable.
# 3. Run in your terminal: uvicorn main:app --reload