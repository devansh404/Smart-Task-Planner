from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import google as genai
import json

app = FastAPI()

class PlanRequest(BaseModel):
    goal: str
    deadline: str | None = None

@app.post("/generate-plan")
def generate_plan(req: PlanRequest):
    """Accepts JSON with `goal` and optional `deadline`. If GEMINI_API_KEY is set
    in environment, forward the request to Gemini (Google Generative Language API).
    Otherwise return a small sample plan as a fallback for local development.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    system_prompt = (
        "You are an expert project manager. Break down the user's goal into a clear, "
        "actionable task plan. Provide a list of tasks with id, name, timeline, "
        "dependencies, and status. Respond with a JSON array."
    )

    if api_key:
        api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
        )

        payload = {
            "contents": [{"parts": [{"text": f'My goal: "{req.goal}". Deadline: {req.deadline or "not specified"}.'}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "responseMimeType": "application/json",
            },
        }

        try:
            resp = requests.post(api_url, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            # Try to extract candidate text
            candidate = data.get("candidates", [None])[0]
            text = None
            if candidate:
                text = candidate.get("content", {}).get("parts", [None])[0]
                if isinstance(text, dict):
                    text = text.get("text")

            if text:
                # Assume the model returned a JSON array as text
                return requests.models.json.loads(text)
            else:
                raise HTTPException(status_code=502, detail="Invalid response from generative API")
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

    # Fallback sample plan when no API key is provided
    sample_plan = [
        {"id": 1, "name": "Define scope and requirements", "timeline": "Day 1-2", "dependencies": [], "status": "Not Started"},
        {"id": 2, "name": "Create wireframes", "timeline": "Day 3-5", "dependencies": ["Define scope and requirements"], "status": "Not Started"},
        {"id": 3, "name": "Develop MVP", "timeline": "Week 2-3", "dependencies": ["Create wireframes"], "status": "Not Started"},
    ]

    return sample_plan


# --- Configuration ---
app = FastAPI()
# Get your API key from environment variables
# For Google, set up GOOGLE_API_KEY in your environment
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# --- Pydantic Models for Request/Response ---
class GoalRequest(BaseModel):
    goal: str

# --- LLM Interaction Logic ---
def generate_plan_from_llm(goal: str) -> dict:
    """
    Generates a task plan by calling the Gemini LLM.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    today = date.today().strftime("%B %d, %Y")

    prompt = f"""
    Analyze the following user goal and break it down into a series of actionable tasks.

    **Goal:** "{goal}"
    **Current Date:** "{today}"

    **Instructions:**
    1. Identify the key phases (e.g., Planning, Development, Launch).
    2. Create a list of specific, actionable tasks for each phase.
    3. For each task, provide a concise description.
    4. Identify dependencies, listing the IDs of tasks that must be completed first. If there are no dependencies, use an empty list.
    5. Calculate a realistic deadline for each task based on the goal's total duration and the current date. The final task's deadline should not exceed the goal's timeline.
    6. Return the output as a single valid JSON object with a key "plan", which contains a list of task objects. Each task object must include: "id" (integer), "task" (string), "description" (string), "dependencies" (list of integers), and "deadline" (string in YYYY-MM-DD format). Do not wrap the JSON in markdown code fences.
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up the response to ensure it's valid JSON
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error processing LLM response: {e}")
        return {"error": "Failed to generate or parse the plan."}

# --- API Endpoint ---
@app.post("/generate-plan")
async def create_plan(request: GoalRequest):
    """
    Accepts a user goal and returns a structured task plan.
    """
    plan = generate_plan_from_llm(request.goal)
    if "error" in plan:
        return {"error": plan["error"]}, 500
    return plan

# To run this app:
# 1. pip install fastapi uvicorn google-generativeai python-dotenv
# 2. Set your GOOGLE_API_KEY environment variable.
# 3. Run in your terminal: uvicorn main:app --reload