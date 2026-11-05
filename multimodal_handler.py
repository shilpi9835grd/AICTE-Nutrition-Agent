"""
AICTE Nutrition Agent — Multimodal Input Handler
Processes food images and grocery label photos using
IBM Granite vision or caption-based analysis.
"""

import base64
import io
import os
from PIL import Image
import httpx
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------------------------
def load_and_resize_image(image_bytes: bytes, max_size: int = 800) -> bytes:
    """
    Resize image to max_size on the longest side to reduce payload,
    convert to JPEG, and return bytes.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def image_to_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


# ---------------------------------------------------------------------------
# Food image description via IBM Granite (text-based caption approach)
# Since Granite-3 is a text model, we use a structured prompt with metadata
# extracted by Pillow and user-provided context.
# ---------------------------------------------------------------------------
def describe_food_image(image_bytes: bytes, user_hint: str = "") -> str:
    """
    Generate a food description from an uploaded image.
    Uses image metadata + user hint to create a structured description
    that is then passed to the nutrition core for analysis.

    Returns a text description of what food items are detected.
    """
    # Process image
    resized = load_and_resize_image(image_bytes)
    img = Image.open(io.BytesIO(resized))
    width, height = img.size

    hint_context = f"The user says: '{user_hint}'" if user_hint else ""

    # Build a description to pass to nutrition analysis
    # In production, you would call an IBM vision model here
    description = f"Food image uploaded ({width}x{height}px). {hint_context}"
    return description


def extract_label_text(image_bytes: bytes) -> str:
    """
    Extract nutritional information from a grocery label image.
    Returns structured text describing the label contents.

    In production, integrate IBM Watson Discovery or a vision model.
    """
    resized = load_and_resize_image(image_bytes)
    img = Image.open(io.BytesIO(resized))
    width, height = img.size

    return f"Nutrition label image uploaded ({width}x{height}px). Please analyze based on visible label."


# ---------------------------------------------------------------------------
# USDA FoodData Central lookup
# ---------------------------------------------------------------------------
USDA_API_BASE = "https://api.nal.usda.gov/fdc/v1"


def search_usda_food(query: str, max_results: int = 5) -> list[dict]:
    """
    Search USDA FoodData Central for a food item.
    Returns a list of food records with nutritional info.
    """
    api_key = os.getenv("USDA_API_KEY", "DEMO_KEY")
    url = f"{USDA_API_BASE}/foods/search"
    params = {
        "query": query,
        "pageSize": max_results,
        "api_key": api_key,
        "dataType": "Foundation,SR Legacy",
    }

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        foods = data.get("foods", [])
        results = []
        for food in foods:
            nutrients = {n["nutrientName"]: n.get("value", 0)
                         for n in food.get("foodNutrients", [])}
            results.append({
                "name": food.get("description", ""),
                "fdcId": food.get("fdcId"),
                "calories": nutrients.get("Energy", nutrients.get("Energy (Atwater General Factors)", 0)),
                "protein_g": nutrients.get("Protein", 0),
                "carbs_g": nutrients.get("Carbohydrate, by difference", 0),
                "fat_g": nutrients.get("Total lipid (fat)", 0),
                "fiber_g": nutrients.get("Fiber, total dietary", 0),
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def format_usda_results(results: list[dict]) -> str:
    """Format USDA search results into a readable string for the LLM."""
    if not results:
        return "No USDA data found."
    if "error" in results[0]:
        return f"USDA lookup error: {results[0]['error']}"

    lines = ["**USDA Nutritional Data (per 100g):**\n"]
    for r in results[:3]:
        lines.append(f"• **{r['name']}**")
        lines.append(f"  Calories: {r['calories']} kcal | Protein: {r['protein_g']}g | "
                     f"Carbs: {r['carbs_g']}g | Fat: {r['fat_g']}g | Fiber: {r['fiber_g']}g")
    return "\n".join(lines)
