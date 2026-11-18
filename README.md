# SnapDiet 🍏 | AI-Driven Premium Nutrition Ecosystem

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42.0-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI%20Powered-8E75C2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Expo](https://img.shields.io/badge/React%20Native-Expo-000020?style=for-the-badge&logo=expo&logoColor=white)](https://expo.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**SnapDiet** is an end-to-end, AI-powered health and nutrition ecosystem tailored for Indian diets, regional cuisines, and smart budgeting. From multimodal food image scanning and intelligent family meal allocation to 24/7 nutrition coaching, SnapDiet simplifies wellness for everyday living.

---

## 🌟 Key Features

### 📊 Central Health Dashboard
* **Dynamic Macro Donut Charts**: Real-time visualization of calories, protein, carbohydrates, and fats consumed vs. personalized daily targets using Plotly.
* **Universal Nutrition Score**: Automatically scores daily diet quality based on adherence to ICMR nutrition standards.
* **Quick Meal Logger**: Natural language meal entry parsed instantly with Google Gemini AI.
* **Smart Hydration Tracker**: Real-time hydration monitoring with progress milestones and adaptive intake guidance.
* **Body Metrics & BMI**: Tracks weight changes, BMI classification, and fitness categories.
* **Gamification & PDF Reports**: Streak tracking, milestone achievements, and 1-click downloadable weekly PDF health reports.

### 📸 AI Meal & Food Scanner
* **Multimodal Image Recognition**: Snap a photo from your webcam/camera or upload meal images.
* **Instant Macro Extraction**: Identifies Indian and international foods, portion sizes, calories, and macronutrients.
* **Packaged Food Auditing**: Calculates health scores, flags hidden sodium/sugars, and recommends healthier alternatives.
* **Seamless Logging**: One-click logging directly into your daily caloric log.

### 🥗 AI Diet & Budget Planner
* **Regional Indian Diet Customization**: Generates personalized meal plans tailored for North, South, East, West, or Mixed Indian cuisines.
* **Budget Meal Generator**: Maximizes nutritional density per rupee spent, optimized for student and family budgets.
* **Leftover Magic**: Suggests creative, healthy recipes based solely on leftover ingredients in your kitchen.

### 👨‍👩‍👧‍👦 Family Nutrition Hub
* **Single-Tap Group Logging**: Enter a collective family meal (e.g., *"Paneer and rotis for 4 people"*), and AI distributes calories and macros proportionally to each family member based on their individual biometrics.
* **Family Health Leaderboard**: Friendly gamified leaderboard tracking streak consistency and nutritional achievements.

### 🤖 Nutri-Bot AI Nutritionist
* **24/7 AI Companion**: Conversational nutrition advice fine-tuned for Indian dietary questions, healthy ingredient substitutions, and meal planning.
* **Token Streaming**: Real-time streaming responses powered by Gemini.
* **Privacy Focused**: Automatically clears chat session history upon user login, logout, and browser refresh.

### 🏋️ AI Workout Routine Planner
* **Personalized 7-Day Splits**: Tailored exercise routines based on fitness level (Cardio, Weightlifting, Yoga, HIIT).

### 👤 Profile & Goal Settings
* **Scientific Metrology**: Calculates Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE) using the clinically validated Mifflin-St Jeor formula.
* **Fully Editable Profile**: Update weight, target weight, activity multiplier, budget, and dietary preferences anytime with instant recalculation.

---

## 🏗️ Project Architecture

```plaintext
SnapDiet/
├── app.py                     # Streamlit Main Application Entrypoint
├── pages/                     # Multi-Page Navigation
│   ├── 0_profile_setup.py     # Profile & Biometric Settings
│   ├── 1_dashboard.py         # Central Health Dashboard & PDF Exporter
│   ├── 2_ai_scanner.py        # Multimodal Gemini Camera/Upload Food Scanner
│   ├── 3_diet_planner.py      # Regional Meal & Budget Planner
│   ├── 4_family_admin.py      # Family Tracking & AI Group Meal Distribution
│   ├── 5_transformation.py    # 90-Day Challenge & Milestones
│   ├── 6_chatbot.py           # Nutri-Bot Conversational Assistant
│   └── 6_workout_planner.py   # AI Fitness Routine Generator
├── utils/                     # Core Business Logic & Helpers
│   ├── ai_engine.py           # Gemini API Integration & Inference
│   ├── db.py                  # SQLite Database & Migration Layer
│   ├── helpers.py             # BMR, TDEE, & Macro Calculation Engines
│   ├── sidebar.py             # Sleek Global Sidebar Navigation
│   └── ui_theme.py            # Glassmorphic Styling & Plotly Visualizations
├── api/                       # Headless REST API (FastAPI)
│   ├── main.py                # FastAPI Server Entrypoint
│   ├── requirements.txt       # API Dependencies
│   └── routes/                # Endpoints for Auth, Diet, and AI
├── mobile/                    # React Native / Expo Mobile App
│   ├── package.json           # Mobile Dependencies
│   └── src/                   # React Native Screens & Components
├── flutter/                   # Flutter Multi-Platform Client
├── requirements.txt           # Python Dependencies for Streamlit
├── vercel.json                # Vercel Serverless Configuration for API
└── run.bat                    # One-Click Windows Startup Script
```

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher
* Git

### 1. Clone the Repository
```bash
git clone https://github.com/maiyashchauhan/SnapDiet.git
cd SnapDiet
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (or use `.streamlit/secrets.toml`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the Application

#### Streamlit Web App (Recommended)
```bash
streamlit run app.py
```
*Or on Windows simply double-click `run.bat`.*

#### FastAPI Backend (Optional)
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
*Or on Windows simply run `run_api.bat`.*

#### Mobile App (Optional)
```bash
cd mobile
npm install
npx expo start
```

---

## ☁️ Deployment

### 1. Streamlit Community Cloud (Free & Recommended for Web UI)
Streamlit Cloud offers native, zero-config hosting with full WebSocket and live session support:
1. Fork or push this repository to your GitHub account.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and connect your GitHub account.
3. Click **"New app"** and select:
   * **Repository**: `maiyashchauhan/SnapDiet`
   * **Branch**: `main`
   * **Main file path**: `app.py`
4. Under **Advanced settings ➔ Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
5. Click **Deploy!**

### 2. Vercel (For REST API Backend)
The repository includes a ready-to-deploy `vercel.json` configured for the FastAPI server:
1. Import the repository in [Vercel](https://vercel.com/new).
2. Set `GEMINI_API_KEY` under Environment Variables.
3. Deploy to get a serverless REST API endpoint at `/api/*`.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Web Frontend** | Streamlit, Plotly, CSS3 Glassmorphism |
| **Mobile Client** | React Native, Expo Router, TypeScript |
| **Multi-platform** | Flutter, Dart |
| **AI & LLM** | Google Gemini (`google-genai` SDK) |
| **Backend API** | FastAPI, Uvicorn, Pydantic |
| **Database** | SQLite3 (Persistent relational storage) |
| **Reporting** | FPDF2 (PDF generation) |

---

## 🔒 Security & Privacy
* **Zero Hardcoded Secrets**: All sensitive API keys are retrieved from environment variables or Streamlit secrets.
* **Ignored Files**: Local databases, environment files (`.env`), and secrets (`secrets.toml`) are omitted from version control via `.gitignore`.
* **Session Privacy**: Personal conversations with Nutri-Bot are ephemeral and automatically cleared upon session reset.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ for National Nutrition Week</p>
