# 🗳️ CivicMate / VoteGuide AI – Smart Election Portal v3.0

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-orange.svg)
![Netlify](https://img.shields.io/badge/Netlify-Deployed-teal.svg)
![Build Status](https://img.shields.io/badge/Tests-14%2F14%20Passed-brightgreen.svg)

**CivicMate / VoteGuide AI** is an intelligent, multi-language democratic election portal and AI-powered assistant designed to streamline voter registration, candidate management, secure voting, live result visualization, and election education.

---

## 📸 Screenshots & UI Showcase

```
+-----------------------------------------------------------------------------------+
| 🗳️ CIVICMATE | Election Portal v3.0                                pradnya [Logout] |
+-------------------------------+---------------------------------------------------+
| 🏠 Home                       |  [ Voters: 250 ]          [ Votes Cast: 1 ]       |
| 📂 Category List              |                                                   |
| 🗳️ Voting List                 |  Welcome, pradnya 👋                               |
| 🤖 AI Assistant               |  +---------------------------------------------+  |
| 📖 Education Center           |  | 🏠 Home - Live election overview            |  |
| 📊 Admin Results              |  | Status: Eligible to Vote (Location: sangli)   |  |
|                               |  +---------------------------------------------+  |
| LANGUAGE: [ English v ]       |  | 📍 Nearby Polling Station (Leaflet OSM Map)   |  |
+-------------------------------+---------------------------------------------------+
```

### 1. 🏠 Main Dashboard & Polling Station Map
Interactive overview featuring live voter counters, status verification checklist, and an embedded **Leaflet OpenStreetMap** showing assigned polling booths.

### 2. 📂 Category Management List
Dynamic election category management (*Student Chairman*, *Student Vice-Chairman*, *Executive Members*) with full **Add**, **Edit**, and **Delete** capabilities.

### 3. 🗳️ Candidate Voting List
Official polling list with candidate profile cards (*Kamal*, *Rajni*, *Shivaji*, *MGR*, *Vijay*). Cast secure votes with real-time double-voting prevention.

### 4. 🤖 AI Assistant & Web Speech Voice Engine
Google Gemini 2.0 Flash powered AI assistant providing election guidance with one-click **`🔊 Speak` audio synthesis**.

### 5. 📖 Interactive Education Center (Multi-Language)
4-Step interactive election walkthrough with **`🔊 Listen` audio buttons** and dynamic translations across **English**, **Marathi (मराठी)**, and **Hindi (हिंदी)**.

### 6. 📊 Dark Theme Admin Portal & Results
Secure password-protected admin portal (`admin123` / `root`) featuring dark theme candidate progress bars, vote percentage fills, and **`Reset Votes`** control.

---

## 🎯 Key Features

- **🐘 PostgreSQL Database Integration**: Persistent storage for voters, candidates, and audit-logged votes connected to PostgreSQL (`postgresql://postgres:root@localhost:5432/voting_system`).
- **🌐 7-Language Indian Localization**: Native translation switching across English, Hindi, Marathi, Bengali, Tamil, Telugu, and Gujarati.
- **🗺️ Leaflet OpenStreetMap**: Interactive polling booth finder with custom map pins and popups.
- **🔊 Web Speech Voice Assistant**: Audio playback for educational guides and AI assistant responses.
- **⚡ Netlify Cloud Ready**: Configured with `netlify.toml` for cloud hosting.

---

## 🧠 System Architecture & Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Voter / Admin
    participant UI as Frontend (CivicMate UI)
    participant Flask as Flask Backend (app.py)
    participant DB as PostgreSQL DB (voting_system)
    participant Gemini as Google Gemini AI

    User->>UI: 1. Select Language / Ask Query / Cast Vote
    alt AI Query
        UI->>Flask: GET /ask?q=query&lang=Marathi
        Flask->>Gemini: Request in target language
        Gemini-->>Flask: Multi-language response
        Flask-->>UI: Return AI answer
    else Secure Vote
        UI->>Flask: POST /vote (Voter ID & Candidate ID)
        Flask->>DB: Check voter status & record vote
        DB-->>Flask: Vote audit logged
        Flask-->>UI: Vote confirmed & update live count
    else Live Results
        UI->>Flask: GET /results
        Flask->>DB: Query candidate vote totals
        DB-->>Flask: Candidate tallies
        Flask-->>UI: Render dark progress bars
    end
```

---

## 🛠️ Technology Stack

| Component | Technology Used |
| :--- | :--- |
| **Backend Framework** | Python 3.11, Flask 3.0 |
| **Database** | PostgreSQL, SQLAlchemy 2.0, Psycopg2 |
| **AI Integration** | Google Gemini 2.0 Flash (`google-generativeai`) |
| **Frontend** | Vanilla HTML5, CSS3 Glassmorphism, JavaScript ES6 |
| **Maps & Audio** | Leaflet OpenStreetMap, Web Speech API |
| **Testing** | Pytest (`14/14 tests passing`) |
| **Deployment** | Netlify (`netlify.toml`) |

---

## ⚙️ Setup & Installation Guide

### 1. Prerequisites
- Python 3.11+
- PostgreSQL Server running locally or in the cloud.

### 2. Local Installation
```bash
# Clone the repository
git clone https://github.com/pradnya1212/Smart-Election-Assistant.git
cd Smart-Election-Assistant/vote_ai

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup (`.env`)
Create a `.env` file or export variables:
```env
DATABASE_URL=postgresql://postgres:root@localhost:5432/voting_system
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
```

### 4. Run Application
```bash
python app.py
```
Open `http://localhost:5000` in your browser.

### 5. Run Test Suite
```bash
python -m pytest test_app.py
```

---

## 🚀 How to Push Changes to GitHub Repository

```bash
# 1. Stage all changed and new files
git add .

# 2. Commit changes with a descriptive message
git commit -m "Add PostgreSQL integration, Netlify config, multi-language support, and 5-screen UI"

# 3. Push to GitHub main branch
git push origin main
```

---

## 🌐 Netlify Cloud Deployment Guide

1. Push your repository to GitHub.
2. Log into [Netlify Dashboard](https://app.netlify.com).
3. Select **Add new site** -> **Import an existing project** -> Choose GitHub repository.
4. Netlify will auto-detect `netlify.toml`. Click **Deploy Site**.
5. Add `DATABASE_URL` and `GEMINI_API_KEY` under **Site configuration** -> **Environment variables**.

---

## 📜 License
Developed for **CivicMate AI Democratic Election Initiative**. Open-source under MIT License.
