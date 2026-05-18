# IPL Hype Hub

An AI-powered, real-time IPL cricket fan engagement platform built with Flask and Google Gemini.

## Features
- 🏏 Live IPL scoreboard simulation with all 10 teams & latest squads
- 🤖 Gemini AI hype man that reacts to fan emoji reactions
- 🌊 Crowd Pulse — agent aggregates all fan reactions into a mutual vibe check
- 📊 Live AI-generated polls & trivia
- 👥 Real fan count (session heartbeat tracking)
- 💾 Fan name remembered across refreshes (localStorage)
- 🌐 All fans see each other's reactions in real-time

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ipl-hype-hub.git
cd ipl-hype-hub

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Gemini API key
cp .env.example .env
# Edit .env and add your key from https://aistudio.google.com/apikey

# 5. Run
python app.py
# Open http://127.0.0.1:5000
```

## Google Cloud Run Deployment

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build & deploy (one command)
gcloud run deploy ipl-hype-hub \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=YOUR_KEY_HERE
```

## Project Structure

```
ipl-hype-hub/
├── app.py              # Flask backend + Gemini AI logic
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container config for Cloud Run
├── .env.example        # Environment variable template
├── templates/
│   └── index.html      # Main HTML template
└── static/
    ├── style.css       # Premium UI styles
    └── app.js          # Frontend logic
```

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key (get it free at aistudio.google.com) |
| `PORT` | Port to run on (default: 8080 for Cloud Run, 5000 locally) |
