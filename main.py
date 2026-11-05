"""
AICTE Nutrition Agent — FastAPI Backend
Exposes REST endpoints consumed by the Streamlit frontend.
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from nutrition_core import (
    generate_meal_plan,
    recommend_food_swaps,
    answer_nutrition_question,
    analyze_food_item,
    adapt_plan_with_feedback,
)
from multimodal_handler import (
    describe_food_image,
    extract_label_text,
    search_usda_food,
    format_usda_results,
)

load_dotenv()

app = FastAPI(
    title="AICTE Nutrition Agent API",
    description="AI-powered personalized nutrition assistant using IBM Granite on watsonx.ai",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request/Response schemas
# ---------------------------------------------------------------------------
class UserProfile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    activity_level: Optional[str] = None   # sedentary / lightly active / moderately active / very active
    goal: Optional[str] = None             # lose weight / gain muscle / maintain / manage diabetes / etc.
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    dietary_preferences: Optional[str] = None  # vegan / vegetarian / keto / halal / etc.
    cuisine_preferences: Optional[str] = None
    disliked_foods: Optional[str] = None
    meals_per_day: Optional[int] = 3


class MealPlanRequest(BaseModel):
    user_profile: UserProfile


class FoodSwapRequest(BaseModel):
    food_item: str
    reason: str
    user_profile: Optional[UserProfile] = None


class NutritionQuestionRequest(BaseModel):
    question: str
    user_profile: Optional[UserProfile] = None


class FeedbackAdaptRequest(BaseModel):
    original_plan: str
    feedback: str
    user_profile: Optional[UserProfile] = None


class USDASearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/", summary="Health check")
def root():
    return {
        "status": "online",
        "agent": "AICTE Nutrition Agent",
        "model": os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-8b-instruct"),
    }


@app.post("/meal-plan", summary="Generate personalized 7-day meal plan")
def meal_plan(req: MealPlanRequest):
    try:
        profile = req.user_profile.model_dump(exclude_none=True)
        result = generate_meal_plan(profile)
        return {"meal_plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/food-swap", summary="Get smart food swap recommendations")
def food_swap(req: FoodSwapRequest):
    try:
        profile = req.user_profile.model_dump(exclude_none=True) if req.user_profile else {}
        result = recommend_food_swaps(req.food_item, req.reason, profile)
        return {"swaps": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", summary="Ask a nutrition question")
def ask_question(req: NutritionQuestionRequest):
    try:
        profile = req.user_profile.model_dump(exclude_none=True) if req.user_profile else {}
        result = answer_nutrition_question(req.question, profile)
        return {"answer": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-food-image", summary="Analyze a food photo or grocery label")
async def analyze_food_image_endpoint(
    file: UploadFile = File(...),
    hint: str = Form(""),
    mode: str = Form("food"),  # "food" or "label"
    user_profile_json: str = Form("{}"),
):
    try:
        import json
        image_bytes = await file.read()

        if mode == "label":
            description = extract_label_text(image_bytes)
        else:
            description = describe_food_image(image_bytes, hint)

        profile = json.loads(user_profile_json) if user_profile_json else {}
        full_description = description
        if hint:
            full_description = f"{description} — Additional context from user: {hint}"

        analysis = analyze_food_item(full_description, profile)
        return {"description": description, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/adapt-plan", summary="Adapt meal plan based on user feedback")
def adapt_plan(req: FeedbackAdaptRequest):
    try:
        profile = req.user_profile.model_dump(exclude_none=True) if req.user_profile else {}
        result = adapt_plan_with_feedback(req.original_plan, req.feedback, profile)
        return {"adapted_plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/usda-search", summary="Search USDA FoodData Central")
def usda_search(req: USDASearchRequest):
    try:
        results = search_usda_food(req.query, req.max_results)
        formatted = format_usda_results(results)
        return {"results": results, "formatted": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )
