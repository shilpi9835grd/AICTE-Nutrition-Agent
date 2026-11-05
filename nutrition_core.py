"""
AICTE Nutrition Agent — Nutrition Core Logic
Handles prompt construction for:
  - Personalized meal plan generation
  - Smart food swap recommendations
  - Nutritional Q&A / contextual explanations
  - Dynamic adaptation based on feedback
"""

from granite_client import generate


# ---------------------------------------------------------------------------
# System persona injected into every prompt
# ---------------------------------------------------------------------------
SYSTEM_PERSONA = """You are "NutriGenie", an expert AI Nutrition Assistant powered by IBM Granite.
You have deep knowledge of:
- Clinical nutrition, dietetics, and sports nutrition
- Cultural cuisines from around the world
- Food allergies, intolerances, and medical dietary requirements
- Macro/micronutrient science
- Weight management, muscle building, and therapeutic diets

Always respond in a warm, empathetic, and professional tone.
Be specific, actionable, and evidence-based. Where relevant, give calorie counts and macros.
Never give medical diagnoses — recommend consulting a doctor for medical concerns.
"""


# ---------------------------------------------------------------------------
# Meal Plan Generation
# ---------------------------------------------------------------------------
def generate_meal_plan(user_profile: dict) -> str:
    """
    Generate a 7-day personalized meal plan based on user profile.

    user_profile keys (all optional):
        name, age, gender, weight_kg, height_cm, activity_level,
        goal, medical_conditions, allergies, dietary_preferences,
        cuisine_preferences, disliked_foods, meals_per_day
    """
    profile_str = _format_profile(user_profile)
    meals_per_day = user_profile.get("meals_per_day", 3)

    prompt = f"""### Task: Generate a 7-Day Personalized Meal Plan

**User Profile:**
{profile_str}

**Instructions:**
1. Create a complete 7-day meal plan with {meals_per_day} meals per day (+ snacks if appropriate).
2. For each meal, list: dish name, approximate calories, key macros (protein/carbs/fat in grams).
3. Respect ALL allergies, intolerances, and dietary restrictions STRICTLY.
4. Incorporate cultural/cuisine preferences where possible.
5. Align meals with the user's health goal.
6. End with a brief "Weekly Nutrition Summary" (avg daily calories, protein, carbs, fat).
7. Add 3 practical meal-prep tips specific to this plan.

Format clearly with day headings (Day 1, Day 2, ...) and meal headings (Breakfast, Lunch, Dinner, Snacks).

### 7-Day Meal Plan:
"""
    return generate(prompt, max_tokens=2048, system=SYSTEM_PERSONA)


# ---------------------------------------------------------------------------
# Food Swap Recommendations
# ---------------------------------------------------------------------------
def recommend_food_swaps(food_item: str, reason: str, user_profile: dict = None) -> str:
    """
    Suggest smart food swaps for a given food item.

    Args:
        food_item: The food the user wants to swap (e.g. "white rice")
        reason: Why they want to swap (e.g. "lower carbs", "vegan", "nut allergy")
        user_profile: Optional context about the user
    """
    profile_context = ""
    if user_profile:
        profile_context = f"\n**User Context:** {_format_profile(user_profile)}\n"

    prompt = f"""{profile_context}### Task: Smart Food Swap Recommendations

The user wants to replace: **{food_item}**
Reason for swap: **{reason}**

**Instructions:**
1. Suggest 5 smart alternatives to "{food_item}".
2. For each swap, provide:
   - Name and brief description
   - Why it's a good swap for the stated reason
   - Approximate calories per 100g / per serving
   - Key nutritional benefit
   - Best used in (cooking context)
3. Highlight the TOP PICK with a ⭐ and explain why it's the best choice.
4. Include one "adventurous" option that the user might not have considered.

### Food Swap Recommendations:
"""
    return generate(prompt, max_tokens=1024, system=SYSTEM_PERSONA)


# ---------------------------------------------------------------------------
# Nutritional Q&A / Contextual Explanations
# ---------------------------------------------------------------------------
def answer_nutrition_question(question: str, user_profile: dict = None) -> str:
    """
    Answer a nutrition question with contextual, personalized explanation.
    """
    profile_context = ""
    if user_profile:
        profile_context = f"\n**User Profile Context:** {_format_profile(user_profile)}\n"

    prompt = f"""{profile_context}### Task: Answer Nutrition Question

**User Question:** {question}

**Instructions:**
- Give a clear, evidence-based answer.
- Use simple language but include scientific reasoning.
- If the question involves a specific food, include its nutritional profile.
- If relevant to the user's profile/goals, personalize the answer.
- If the question involves a medical condition, recommend professional consultation.
- Keep the answer focused and under 300 words unless detail is needed.

### Answer:
"""
    return generate(prompt, max_tokens=800, system=SYSTEM_PERSONA)


# ---------------------------------------------------------------------------
# Analyze Food from Description / Image Caption
# ---------------------------------------------------------------------------
def analyze_food_item(food_description: str, user_profile: dict = None) -> str:
    """
    Analyze a food item (described via text or extracted from image).
    Returns nutritional breakdown and recommendation.
    """
    profile_context = ""
    if user_profile:
        profile_context = f"\n**User Context:** {_format_profile(user_profile)}\n"

    prompt = f"""{profile_context}### Task: Food Analysis & Recommendation

**Food Item / Description:** {food_description}

**Instructions:**
1. Identify the food item(s) present.
2. Provide a detailed nutritional breakdown (per serving):
   - Calories, Protein, Carbohydrates (total + fiber + sugars), Fat (total + saturated), Sodium, Key vitamins/minerals
3. Rate the food on a Health Score (1–10) with brief justification.
4. List 3 health benefits.
5. List 2 potential concerns (if any).
6. Give a personalized recommendation: Should the user eat this? How often? Any modifications?
7. Suggest one way to make this food healthier.

### Food Analysis:
"""
    return generate(prompt, max_tokens=900, system=SYSTEM_PERSONA)


# ---------------------------------------------------------------------------
# Dynamic Feedback Adaptation
# ---------------------------------------------------------------------------
def adapt_plan_with_feedback(original_plan: str, feedback: str, user_profile: dict = None) -> str:
    """
    Adapt an existing meal plan based on user feedback.
    """
    profile_context = ""
    if user_profile:
        profile_context = f"\n**User Profile:** {_format_profile(user_profile)}\n"

    prompt = f"""{profile_context}### Task: Adapt Meal Plan Based on User Feedback

**Original Meal Plan (summary):**
{original_plan[:1500]}

**User Feedback:** {feedback}

**Instructions:**
1. Acknowledge the feedback empathetically.
2. Identify which parts of the plan need adjustment.
3. Provide the revised meals/days that address the feedback.
4. Explain why each change was made.
5. Confirm the revised plan still meets the user's health goals.

### Adapted Plan:
"""
    return generate(prompt, max_tokens=1200, system=SYSTEM_PERSONA)


# ---------------------------------------------------------------------------
# Helper: Format user profile dict → readable string
# ---------------------------------------------------------------------------
def _format_profile(profile: dict) -> str:
    lines = []
    field_labels = {
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "weight_kg": "Weight (kg)",
        "height_cm": "Height (cm)",
        "activity_level": "Activity Level",
        "goal": "Health Goal",
        "medical_conditions": "Medical Conditions",
        "allergies": "Allergies/Intolerances",
        "dietary_preferences": "Dietary Preferences",
        "cuisine_preferences": "Cuisine Preferences",
        "disliked_foods": "Disliked Foods",
        "meals_per_day": "Meals per Day",
    }
    for key, label in field_labels.items():
        val = profile.get(key)
        if val:
            lines.append(f"- {label}: {val}")
    return "\n".join(lines) if lines else "No profile provided."
