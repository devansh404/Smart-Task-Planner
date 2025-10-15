from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import google as genai
import json

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