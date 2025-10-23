import os
from google import genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

def generate_plan_from_llm(goal: str, deadline: str) -> dict:
    """
    Generates a task plan by calling the Gemini LLM.
    """

    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an expert project manager. Analyze the following user goal and break it down into a series of simple actionable tasks.

    **Goal:** "{goal}"
    **Deadline:** "{deadline}"

    **Instructions:**
    1. Divide the goal into manageable tasks.
    2. For each task, provide a concise description.
    3. Calculate a realistic timeline for each task based on the goal's total duration. The final task's timeline should not exceed the goal's deadline.
    4. Return the output as a single valid JSON object which contains a list of task objects. Each task object must include: "id" (integer), "name" (string), "description" (string), and "timeline" (string in HH hours/DD days format).
    Do not wrap the JSON in markdown code fences.
    Following is the example JSON format for each task object:
    [
        {{
        "id": 1,
        "name": "Define MVP & acceptance criteria",
        "description": "Write concise scope and success metrics for the launch.",
        "timeline": "4 hours"
        }},
        {{
        "id": 2,
        "name": "Wireframes & user flow",
        "description": "Design the basic layout and flow of user screens.",
        "timeline": "6 hours"
        }},
        {{
        "id": 3,
        "name": "Backend APIs & database schema",
        "description": "Implement core API endpoints and schema for products and users.",
        "timeline": "2 days"
        }}
    ]
    and output text should be in the above format only.
    """
    try:
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
        )
        print(response)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        print(cleaned_response)
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

# --- API Endpoint ---
class GoalRequest(BaseModel):
    goal: str
    deadline: str

# --- API Endpoint ---
@app.post("/generate-plan")
async def create_plan(request: GoalRequest):
    """
    Accepts a user goal and returns a structured task plan.
    """
    res = generate_plan_from_llm(request.goal, request.deadline)

    def map_item(item: dict) -> dict:
        if not isinstance(item, dict):
            return {"name": str(item), "timeline": ""}
        id = item.get("id")
        name = item.get("name")
        description = item.get("description")
        timeline = item.get("timeline")
        return {"id": id, "name": name, "description": description, "timeline": timeline}

    data: list[dict] = [map_item(it) for it in res]
    return data
