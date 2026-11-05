# 🥗 NutriGenie — AI Nutrition Agent
### AICTE AI Challenge · Problem Statement #8

> *"The Smartest AI Nutrition Assistant"* — Personalized, adaptive, multimodal nutrition guidance powered by **IBM Granite** on **IBM watsonx.ai**.

---

## 🌟 Features

| Feature | Description |
|---|---|
| 💬 **Conversational Q&A** | Ask any nutrition question — get evidence-based, personalized answers |
| 📅 **7-Day Meal Planner** | AI-generated meal plans tailored to goals, allergies, culture & medical conditions |
| 🔄 **Smart Food Swaps** | Intelligent alternatives with nutritional comparisons and reasoning |
| 📸 **Food Image Analysis** | Upload a food photo or grocery label for instant nutritional breakdown |
| 🔁 **Adaptive Feedback** | Refine your meal plan with natural language feedback |
| 📊 **USDA Database** | Real-time lookup from USDA FoodData Central |
| 👤 **User Profiles** | Persistent health profiles: goals, allergies, dietary preferences, medical conditions |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (app.py)               │
│  Chat | Meal Planner | Food Swaps | Image Analysis | USDA   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP REST (httpx)
┌─────────────────────▼───────────────────────────────────────┐
│                  FastAPI Backend (main.py)                    │
│  /ask  /meal-plan  /food-swap  /analyze-food-image          │
│  /adapt-plan  /usda-search                                   │
└──────────────┬────────────────────────┬─────────────────────┘
               │                        │
┌──────────────▼────────────┐  ┌────────▼────────────────────┐
│   IBM Granite on          │  │   USDA FoodData Central      │
│   watsonx.ai              │  │   API (free, optional)       │
│   (granite_client.py)     │  │   (multimodal_handler.py)   │
│                           │  └─────────────────────────────┘
│   ibm/granite-3-8b-instruct│
└───────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd AICTE_Nutrition_Agent
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_watsonx_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-3-8b-instruct

# Optional — for USDA food database search
USDA_API_KEY=your_usda_api_key_here
```

### 3. Get IBM Credentials (Free Lite Account)

1. Sign up at [IBM Cloud](https://cloud.ibm.com) (Lite tier is free)
2. Create a **watsonx.ai** instance
3. Go to **IAM → API Keys** → Create an API key → copy to `IBM_API_KEY`
4. Open your watsonx.ai project → copy the **Project ID** → paste to `IBM_PROJECT_ID`
5. (Optional) Get a free USDA API key at [fdc.nal.usda.gov](https://fdc.nal.usda.gov/api-guide.html)

### 4. Run the Application

**Terminal 1 — Start the backend:**
```bash
python main.py
```
Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

**Terminal 2 — Start the frontend:**
```bash
streamlit run app.py
```
Frontend runs at: http://localhost:8501

---

## 📁 Project Structure

```
AICTE_Nutrition_Agent/
├── main.py                  # FastAPI backend — all REST endpoints
├── app.py                   # Streamlit frontend — full interactive UI
├── granite_client.py        # IBM Granite / watsonx.ai client
├── nutrition_core.py        # Prompt engineering & nutrition logic
├── multimodal_handler.py    # Image processing & USDA API integration
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
└── README.md                # This file
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check & model info |
| `POST` | `/meal-plan` | Generate 7-day personalized meal plan |
| `POST` | `/food-swap` | Get smart food swap recommendations |
| `POST` | `/ask` | Ask any nutrition question |
| `POST` | `/analyze-food-image` | Analyze food photo or grocery label |
| `POST` | `/adapt-plan` | Adapt meal plan with feedback |
| `POST` | `/usda-search` | Search USDA FoodData Central |

Interactive API documentation: **http://localhost:8000/docs**

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **AI Model** | IBM Granite 3 (8B Instruct) via IBM watsonx.ai |
| **IBM Service** | IBM Cloud Lite — watsonx.ai |
| **Backend** | Python · FastAPI · Uvicorn |
| **Frontend** | Streamlit |
| **Image Processing** | Pillow |
| **HTTP Client** | httpx |
| **Food Database** | USDA FoodData Central API |
| **Config** | python-dotenv · pydantic-settings |

---

## 🎯 How It Works

### Personalization Engine
The system builds a rich user context (age, weight, goals, allergies, culture, medical conditions) that is injected into every IBM Granite prompt, ensuring responses are always personalized rather than generic.

### Prompt Engineering
Each feature uses carefully crafted, role-specific prompts:
- **System persona**: NutriGenie is established as an expert dietitian with empathy
- **Structured output**: Prompts request specific formats (macros, health scores, day-by-day plans)
- **Safety guardrails**: Medical advice boundaries are enforced in the system prompt

### Multimodal Input
- **Food photos**: Uploaded images are resized, described, and analyzed
- **Grocery labels**: Label images are processed for nutritional extraction
- **Text descriptions**: Natural language food descriptions trigger full nutritional analysis

### Adaptive Learning
The feedback adaptation loop allows users to iteratively refine their meal plans by providing natural language feedback, which Granite uses to make targeted adjustments while preserving the plan's nutritional integrity.

---

## 📄 License

MIT License — Built for the AICTE AI Challenge 2024-25.

---

*NutriGenie is not a substitute for professional medical or dietary advice. Always consult a registered dietitian for clinical nutrition guidance.*
