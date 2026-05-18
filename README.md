# 🏏 IPL Hype Hub

> **The ultimate AI-powered second-screen experience for IPL cricket fans.**  
> React in real-time. Feel the crowd. Let the AI hype you up.

---

## 📌 What is IPL Hype Hub?

IPL Hype Hub is a **live fan engagement platform** built for the Indian Premier League. Instead of watching cricket alone, fans join a shared virtual stadium — reacting with emojis, seeing everyone else's emotions in real-time, and getting hyped up by a Gemini AI agent that reads the crowd's mood and responds automatically.

It transforms passive viewing into an active, community-driven experience — like being in a stadium with thousands of fans, from your phone or laptop.

---

## ✨ Features

### 🎯 Core Experience
| Feature | Description |
|---|---|
| **Live Scoreboard** | Real-time IPL match simulation with all 10 teams, actual player names, overs, wickets, and last ball events |
| **Emoji Reactions** | 8 one-tap reactions (🔥🏏😱👏💔🚀😂💪) — visible to all connected fans instantly |
| **AI Hype Bot** | Gemini AI agent that reacts automatically to individual fan reactions with cricket-specific hype lines |
| **🌊 Crowd Pulse** | Agent aggregates ALL fan reactions, detects the dominant mood, and posts a single crowd-wide summary |
| **Live Trivia** | AI-generated IPL trivia questions with real player/team context — answer to reveal a fun fact |
| **Live Polls** | AI-generated fan polls specific to the current match and squad |

### 👥 Social & Real-time
| Feature | Description |
|---|---|
| **Real Fan Count** | Shows actual number of connected browsers (session heartbeat, 30s timeout) — not a fake number |
| **Global Reaction Sync** | Every fan's emoji reaction floats up on every other connected screen simultaneously |
| **Crowd Sentiment Bar** | Live breakdown of crowd mood — 🔥 Hype / 😊 Happy / 😬 Nervous / 😤 Angry |
| **Hype Meter** | Sidebar bar that rises and glows as the crowd energy increases |

### 🤖 AI Agent System
| Action | What Gemini Does |
|---|---|
| `Crazy Play!` | Generates a wild reaction to an imagined insane match moment |
| `Roast Rival` | Friendly savage roast of the opposing team using actual player names |
| `Chant` | Creates a rhyming, ALL-CAPS stadium chant for your team |
| `Meme Drop` | Describes a perfect IPL internet meme for the moment |
| `Vibe Check` | One-sentence crowd mood report based on current hype level |
| Auto-reaction | Fires automatically every Nth fan emoji (N scales with real fan count) |
| Crowd Pulse | Fires after every `fans × 3` reactions with a full crowd summary |

### 💾 Quality of Life
- **Name remembered** across page refreshes via `localStorage`
- **No text box** — pure emoji-driven interaction
- **Works without API** — smart pre-built fallbacks for every AI feature
- **Session tracking** — each browser tab has a unique ID

---

## 🏗️ Architecture

```
Browser (Fan)
    │
    ├── GET /sync?last_id=&last_reaction_id=&sid=&fan=   ← polls every 1.5s
    ├── POST /react  { emoji, sender }
    ├── POST /chat   { message, team, sender }
    ├── POST /action { action, team }
    ├── GET  /trivia?team=
    └── GET  /poll?team=
            │
            ▼
      Flask Backend (app.py)
            │
            ├── Global State (in-memory)
            │     ├── chat_messages[]        ← ID-based, all clients track last_id
            │     ├── reactions_log[]        ← ID-based, all clients track last_reaction_id
            │     ├── active_sessions{}      ← {sid: (name, timestamp)} for real fan count
            │     ├── crowd_reaction_buffer  ← rolling window for Crowd Pulse
            │     └── score_data{}           ← simulated live match state
            │
            └── Gemini AI (google-genai SDK)
                  └── model: gemini-2.0-flash
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Flask |
| **AI** | Google Gemini (`gemini-2.0-flash`) via `google-genai` SDK |
| **Frontend** | Vanilla HTML5 / CSS3 / JavaScript (no framework) |
| **Fonts** | Google Fonts — Outfit |
| **Deployment** | Google Cloud Run (Docker + gunicorn) |
| **State** | In-memory (single worker — see note below) |
| **Auth** | Fan name only — stored in `localStorage` |

> **Note on state:** The app uses in-memory global state. This works perfectly with `--workers 1` in gunicorn (Cloud Run). For multi-instance scaling, a Redis layer would be needed.

---

## 📂 Project Structure

```
ipl-hype-hub/
├── app.py                  # Flask routes, Gemini AI, match simulation, crowd logic
├── requirements.txt        # Python dependencies
├── Dockerfile              # Cloud Run container
├── .dockerignore
├── .gitignore
├── .env.example            # Template — copy to .env and fill in key
├── README.md
├── templates/
│   └── index.html          # Single-page UI (Jinja2)
└── static/
    ├── style.css           # Glassmorphic dark-mode UI
    └── app.js              # Client-side sync, reactions, widgets
```

---

## ⚡ Local Setup

```bash
# 1. Clone
git clone https://github.com/imadhurgupta/apl.git
cd apl

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
copy .env.example .env
# Open .env and paste your key from https://aistudio.google.com/apikey

# 5. Run
python app.py
# → http://127.0.0.1:5000
```

---

## ☁️ Deploy to Google Cloud Run

```powershell
# One-time setup
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ipl-hype-hub

# Deploy
gcloud run deploy ipl-hype-hub `
  --image gcr.io/YOUR_PROJECT_ID/ipl-hype-hub `
  --region asia-south1 `
  --allow-unauthenticated `
  --port 8080 `
  --memory 512Mi `
  --set-env-vars GEMINI_API_KEY=YOUR_KEY_HERE
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Gemini API key from [aistudio.google.com](https://aistudio.google.com/apikey) |
| `PORT` | No | Port to bind (default: 5000 local, 8080 Cloud Run auto-sets this) |
| `ENVIRONMENT` | No | Set to `production` to disable Flask debug mode |

---

## 🏟️ IPL Teams Supported

All 10 current IPL franchises with 2024–25 squad data:

`CSK` `MI` `RCB` `KKR` `SRH` `RR` `DC` `PBKS` `LSG` `GT`

AI responses reference actual player names for roasts, cheers, trivia, and crowd reactions.

---

## 📄 License

MIT — build on it, remix it, use it at your next IPL watch party. 🏏
