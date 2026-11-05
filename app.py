"""
AICTE Nutrition Agent — Streamlit Frontend
Interactive chat-style UI with meal planning, food swap, Q&A, and image analysis.
"""

import streamlit as st
import httpx
import json
import os
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NutriGenie — AI Nutrition Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a7a4a 0%, #2ecc71 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p { margin: 0.3rem 0 0; opacity: 0.9; }
    .metric-card {
        background: #f0faf4;
        border: 1px solid #b7e4c7;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .chat-message {
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .user-message { background: #e8f4fd; border-left: 4px solid #3b82d4; }
    .ai-message { background: #f0faf4; border-left: 4px solid #2ecc71; }
    .stButton > button {
        background-color: #1a7a4a;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover { background-color: #145c38; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "current_meal_plan" not in st.session_state:
    st.session_state.current_meal_plan = ""


# ---------------------------------------------------------------------------
# Helper: call backend
# ---------------------------------------------------------------------------
def call_api(endpoint: str, payload: dict, timeout: float = 120.0) -> dict:
    try:
        resp = httpx.post(f"{BACKEND_URL}/{endpoint}", json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"API error {e.response.status_code}: {e.response.text}"}
    except httpx.ConnectError:
        return {"error": "Cannot connect to backend. Make sure `python main.py` is running."}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Sidebar — User Profile
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 👤 Your Profile")
    st.caption("Fill in your details for personalized recommendations.")

    with st.form("profile_form"):
        name = st.text_input("Name", placeholder="e.g. Priya")
        col1, col2 = st.columns(2)
        age = col1.number_input("Age", 10, 100, 25)
        gender = col2.selectbox("Gender", ["", "Female", "Male", "Non-binary", "Prefer not to say"])

        col3, col4 = st.columns(2)
        weight = col3.number_input("Weight (kg)", 30.0, 250.0, 65.0, step=0.5)
        height = col4.number_input("Height (cm)", 100.0, 250.0, 165.0, step=0.5)

        activity = st.selectbox("Activity Level", [
            "Sedentary (desk job, no exercise)",
            "Lightly Active (1-3 days/week exercise)",
            "Moderately Active (3-5 days/week exercise)",
            "Very Active (6-7 days/week intense exercise)",
            "Athlete (2x/day training)",
        ])

        goal = st.selectbox("Health Goal", [
            "Lose Weight",
            "Gain Muscle",
            "Maintain Weight",
            "Manage Diabetes (Type 2)",
            "Lower Cholesterol",
            "Improve Gut Health",
            "Boost Energy",
            "Sports Performance",
            "Pregnancy Nutrition",
            "Heart Health",
        ])

        allergies = st.text_input("Allergies / Intolerances",
                                  placeholder="e.g. peanuts, lactose, gluten")
        dietary_pref = st.multiselect("Dietary Preferences", [
            "Vegetarian", "Vegan", "Pescatarian", "Keto", "Paleo",
            "Halal", "Kosher", "Low-FODMAP", "Mediterranean", "Jain",
        ])
        cuisine = st.text_input("Cuisine Preferences",
                                placeholder="e.g. Indian, Mediterranean, Japanese")
        medical = st.text_input("Medical Conditions",
                                placeholder="e.g. Type 2 diabetes, hypertension")
        dislikes = st.text_input("Disliked Foods",
                                 placeholder="e.g. broccoli, tofu")
        meals_day = st.slider("Meals per Day", 2, 6, 3)

        save_btn = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if save_btn:
        st.session_state.user_profile = {
            k: v for k, v in {
                "name": name,
                "age": age,
                "gender": gender,
                "weight_kg": weight,
                "height_cm": height,
                "activity_level": activity,
                "goal": goal,
                "allergies": allergies,
                "dietary_preferences": ", ".join(dietary_pref) if dietary_pref else "",
                "cuisine_preferences": cuisine,
                "medical_conditions": medical,
                "disliked_foods": dislikes,
                "meals_per_day": meals_day,
            }.items() if v
        }
        st.success("✅ Profile saved!")

    if st.session_state.user_profile:
        st.markdown("---")
        st.markdown("**Active Profile:**")
        p = st.session_state.user_profile
        if p.get("name"):
            st.markdown(f"👤 **{p['name']}** | {p.get('age', '?')}y | {p.get('gender', '')}")
        st.markdown(f"🎯 Goal: `{p.get('goal', 'Not set')}`")
        if p.get("allergies"):
            st.markdown(f"⚠️ Allergies: `{p['allergies']}`")

    # Backend status
    st.markdown("---")
    try:
        status = httpx.get(f"{BACKEND_URL}/", timeout=3.0).json()
        st.success(f"🟢 Backend online\n`{status.get('model', 'IBM Granite')}`")
    except Exception:
        st.error("🔴 Backend offline\nRun: `python main.py`")


# ---------------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🥗 NutriGenie</h1>
    <p>Your AI-powered personal nutrition assistant — powered by IBM Granite on watsonx.ai</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Ask NutriGenie",
    "📅 Meal Planner",
    "🔄 Food Swaps",
    "📸 Analyze Food",
    "📊 Nutrition Lookup",
])


# ============================================================
# TAB 1 — Chat / Q&A
# ============================================================
with tab1:
    st.markdown("### 💬 Ask NutriGenie Anything")
    st.caption("Ask nutrition questions, get personalized advice, or explore food science.")

    # Chat history display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-message user-message">🧑 <strong>You:</strong> {msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message ai-message">🤖 <strong>NutriGenie:</strong><br>{msg["content"]}</div>',
                    unsafe_allow_html=True
                )

    # Suggested questions
    st.markdown("**💡 Try asking:**")
    suggestions = [
        "Why is quinoa better than white rice for weight loss?",
        "What should I eat before a morning workout?",
        "How much protein do I need daily?",
        "What are good iron-rich foods for vegetarians?",
    ]
    cols = st.columns(2)
    for i, sug in enumerate(suggestions):
        if cols[i % 2].button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state._quick_question = sug

    with st.form("chat_form", clear_on_submit=True):
        default_q = getattr(st.session_state, "_quick_question", "")
        user_input = st.text_area(
            "Your question:",
            value=default_q,
            placeholder="e.g. What is the best breakfast for someone with Type 2 diabetes?",
            height=80,
        )
        send_btn = st.form_submit_button("🚀 Ask NutriGenie", use_container_width=True)

    if send_btn and user_input.strip():
        if hasattr(st.session_state, "_quick_question"):
            del st.session_state._quick_question
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("NutriGenie is thinking..."):
            result = call_api("ask", {
                "question": user_input,
                "user_profile": st.session_state.user_profile or None,
            })
        answer = result.get("answer", result.get("error", "Error occurred."))
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()


# ============================================================
# TAB 2 — Meal Planner
# ============================================================
with tab2:
    st.markdown("### 📅 Generate Your Personalized 7-Day Meal Plan")
    st.caption("Uses your saved profile. Adjust preferences below for this session if needed.")

    with st.expander("⚙️ Override for this plan only", expanded=False):
        override_goal = st.text_input("Override Goal", placeholder="Leave blank to use profile goal")
        override_allergies = st.text_input("Override Allergies", placeholder="Leave blank to use profile")
        override_pref = st.text_input("Override Dietary Preference")

    if st.button("🍽️ Generate 7-Day Meal Plan", use_container_width=True, type="primary"):
        profile = dict(st.session_state.user_profile)
        if override_goal:
            profile["goal"] = override_goal
        if override_allergies:
            profile["allergies"] = override_allergies
        if override_pref:
            profile["dietary_preferences"] = override_pref

        if not profile:
            st.warning("⚠️ Please fill in your profile in the sidebar for a personalized plan.")

        with st.spinner("🧠 NutriGenie is crafting your personalized meal plan with IBM Granite..."):
            result = call_api("meal-plan", {"user_profile": profile})

        if "error" in result:
            st.error(result["error"])
        else:
            st.session_state.current_meal_plan = result["meal_plan"]
            st.success("✅ Your 7-Day Meal Plan is ready!")

    if st.session_state.current_meal_plan:
        st.markdown("---")
        st.markdown(st.session_state.current_meal_plan)

        # Feedback & adaptation
        st.markdown("---")
        st.markdown("### 🔁 Adapt This Plan")
        with st.form("feedback_form"):
            feedback = st.text_area(
                "Tell NutriGenie what to change:",
                placeholder="e.g. I don't like the Tuesday dinner. Replace all fish with chicken. Monday lunch is too heavy.",
                height=80,
            )
            adapt_btn = st.form_submit_button("🔄 Adapt Plan", use_container_width=True)

        if adapt_btn and feedback.strip():
            with st.spinner("Adapting your plan..."):
                result = call_api("adapt-plan", {
                    "original_plan": st.session_state.current_meal_plan,
                    "feedback": feedback,
                    "user_profile": st.session_state.user_profile or None,
                })
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.current_meal_plan = result["adapted_plan"]
                st.success("✅ Plan adapted!")
                st.rerun()

        # Download
        st.download_button(
            "⬇️ Download Meal Plan",
            data=st.session_state.current_meal_plan,
            file_name="my_nutrigenie_meal_plan.txt",
            mime="text/plain",
        )


# ============================================================
# TAB 3 — Food Swaps
# ============================================================
with tab3:
    st.markdown("### 🔄 Smart Food Swap Recommendations")
    st.caption("Find healthier, tastier, or diet-compliant alternatives to any food.")

    with st.form("swap_form"):
        col1, col2 = st.columns(2)
        food_item = col1.text_input("Food to Replace", placeholder="e.g. white rice, butter, sugar")
        reason = col2.text_input(
            "Reason for Swap",
            placeholder="e.g. lose weight, vegan diet, nut allergy, lower sodium",
        )
        swap_btn = st.form_submit_button("🔍 Find Swaps", use_container_width=True)

    if swap_btn and food_item and reason:
        with st.spinner("Finding the best swaps..."):
            result = call_api("food-swap", {
                "food_item": food_item,
                "reason": reason,
                "user_profile": st.session_state.user_profile or None,
            })
        if "error" in result:
            st.error(result["error"])
        else:
            st.markdown(result["swaps"])
    elif swap_btn:
        st.warning("Please enter both a food item and the reason for swapping.")


# ============================================================
# TAB 4 — Analyze Food (Image / Text)
# ============================================================
with tab4:
    st.markdown("### 📸 Analyze a Food Item or Grocery Label")
    st.caption("Upload a photo or describe what you're eating to get a full nutritional analysis.")

    analysis_mode = st.radio(
        "Input Method:",
        ["📝 Describe the food (text)", "🖼️ Upload food photo", "🏷️ Upload grocery label"],
        horizontal=True,
    )

    user_hint = ""
    image_bytes = None

    if analysis_mode == "📝 Describe the food (text)":
        user_hint = st.text_area(
            "Describe the food:",
            placeholder="e.g. A bowl of chicken tikka masala with basmati rice and naan bread",
            height=80,
        )
        analyze_btn = st.button("🔬 Analyze", use_container_width=True)
        do_image = False

    else:
        upload_label = "Upload food photo" if "photo" in analysis_mode else "Upload grocery label photo"
        uploaded = st.file_uploader(upload_label, type=["jpg", "jpeg", "png", "webp"])
        user_hint = st.text_input("Additional context (optional):",
                                  placeholder="e.g. This is a restaurant pasta dish")
        if uploaded:
            image_bytes = uploaded.read()
            st.image(image_bytes, caption="Uploaded image", width=300)
        analyze_btn = st.button("🔬 Analyze", use_container_width=True)
        do_image = True

    if analyze_btn:
        if analysis_mode == "📝 Describe the food (text)" and user_hint.strip():
            with st.spinner("Analyzing food..."):
                result = call_api("ask", {
                    "question": f"Analyze this food and give a full nutritional breakdown, health score, benefits, and recommendation: {user_hint}",
                    "user_profile": st.session_state.user_profile or None,
                })
            if "error" in result:
                st.error(result["error"])
            else:
                st.markdown(result["answer"])

        elif do_image and image_bytes:
            with st.spinner("Analyzing image..."):
                mode = "label" if "label" in analysis_mode else "food"
                files = {"file": ("food_image.jpg", image_bytes, "image/jpeg")}
                data = {
                    "hint": user_hint,
                    "mode": mode,
                    "user_profile_json": json.dumps(st.session_state.user_profile or {}),
                }
                try:
                    resp = httpx.post(
                        f"{BACKEND_URL}/analyze-food-image",
                        files=files,
                        data=data,
                        timeout=120.0,
                    )
                    resp.raise_for_status()
                    result = resp.json()
                    st.markdown("**Image Description:**")
                    st.info(result.get("description", ""))
                    st.markdown("---")
                    st.markdown(result.get("analysis", ""))
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please provide input before analyzing.")


# ============================================================
# TAB 5 — Nutrition Lookup (USDA)
# ============================================================
with tab5:
    st.markdown("### 📊 Nutrition Database Lookup")
    st.caption("Search the USDA FoodData Central database for accurate nutritional data.")

    with st.form("usda_form"):
        query = st.text_input("Search for a food:", placeholder="e.g. avocado, brown rice, salmon")
        search_btn = st.form_submit_button("🔍 Search USDA Database", use_container_width=True)

    if search_btn and query:
        with st.spinner("Searching USDA FoodData Central..."):
            result = call_api("usda-search", {"query": query, "max_results": 5})

        if "error" in result:
            st.error(result["error"])
        else:
            st.markdown(result.get("formatted", ""))
            foods = result.get("results", [])
            if foods and "error" not in foods[0]:
                st.markdown("#### Detailed Results")
                for food in foods:
                    with st.expander(f"**{food['name']}**"):
                        cols = st.columns(5)
                        cols[0].metric("Calories", f"{food['calories']:.0f} kcal")
                        cols[1].metric("Protein", f"{food['protein_g']:.1f}g")
                        cols[2].metric("Carbs", f"{food['carbs_g']:.1f}g")
                        cols[3].metric("Fat", f"{food['fat_g']:.1f}g")
                        cols[4].metric("Fiber", f"{food['fiber_g']:.1f}g")

                        analyze_this = st.button(
                            f"🔬 Ask NutriGenie about {food['name'][:30]}...",
                            key=f"analyze_{food['fdcId']}",
                        )
                        if analyze_this:
                            with st.spinner("Getting NutriGenie's take..."):
                                res = call_api("ask", {
                                    "question": f"Tell me about the health benefits and best uses of {food['name']}",
                                    "user_profile": st.session_state.user_profile or None,
                                })
                            st.markdown(res.get("answer", res.get("error", "")))


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8rem;'>"
    "🥗 NutriGenie · Powered by <strong>IBM Granite</strong> on watsonx.ai · "
    "AICTE AI Challenge · Not a substitute for professional medical advice"
    "</div>",
    unsafe_allow_html=True,
)
