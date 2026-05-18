import os
import random
import json
from flask import Flask, request, jsonify, render_template
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_ID = "gemini-2.0-flash"

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None
    print("[WARNING] GEMINI_API_KEY not set — running in mock mode.")

def generate(prompt: str) -> str:
    """Call Gemini and return plain text. Raises on failure."""
    resp = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return resp.text.strip()

# ──────────────────────────────────────────────
# Global App State
# ──────────────────────────────────────────────
current_hype = 20
sentiment_breakdown = {"hype": 40, "nervous": 30, "angry": 15, "happy": 15}
chat_messages = []
reactions_log = []   # Stores ALL reactions with IDs — each client tracks its own last_reaction_id
reaction_id_counter = 0
msg_id_counter = 0
connected_fans = random.randint(120, 400)  # Simulated viewer count

# ──────────────────────────────────────────────
# IPL Team Database
# ──────────────────────────────────────────────
IPL_TEAMS = {
    "CSK": {
        "full_name": "Chennai Super Kings",
        "color": "#f5a623",
        "squad": ["Ruturaj Gaikwad", "MS Dhoni", "Ravindra Jadeja", "Shivam Dube",
                  "Matheesha Pathirana", "Rachin Ravindra", "Deepak Chahar",
                  "Moeen Ali", "Tushar Deshpande", "Sameer Rizvi", "Ajinkya Rahane"]
    },
    "MI": {
        "full_name": "Mumbai Indians",
        "color": "#004c93",
        "squad": ["Rohit Sharma", "Hardik Pandya", "Jasprit Bumrah", "Suryakumar Yadav",
                  "Ishan Kishan", "Tim David", "Gerald Coetzee", "Naman Dhir",
                  "Romario Shepherd", "Tilak Varma", "Piyush Chawla"]
    },
    "RCB": {
        "full_name": "Royal Challengers Bengaluru",
        "color": "#c8102e",
        "squad": ["Virat Kohli", "Faf du Plessis", "Glenn Maxwell", "Mohammed Siraj",
                  "Rajat Patidar", "Cameron Green", "Dinesh Karthik", "Reece Topley",
                  "Yash Dayal", "Mahipal Lomror", "Alzarri Joseph"]
    },
    "KKR": {
        "full_name": "Kolkata Knight Riders",
        "color": "#3a225d",
        "squad": ["Shreyas Iyer", "Andre Russell", "Sunil Narine", "Rinku Singh",
                  "Mitchell Starc", "Phil Salt", "Varun Chakaravarthy", "Angkrish Raghuvanshi",
                  "Venkatesh Iyer", "Harshit Rana", "Ramandeep Singh"]
    },
    "SRH": {
        "full_name": "Sunrisers Hyderabad",
        "color": "#f26522",
        "squad": ["Pat Cummins", "Travis Head", "Abhishek Sharma", "Heinrich Klaasen",
                  "Bhuvneshwar Kumar", "T Natarajan", "Nitish Reddy", "Aiden Markram",
                  "Jaydev Unadkat", "Shahbaz Ahmed", "Adam Zampa"]
    },
    "RR": {
        "full_name": "Rajasthan Royals",
        "color": "#e83283",
        "squad": ["Sanju Samson", "Jos Buttler", "Yashasvi Jaiswal", "Yuzvendra Chahal",
                  "Trent Boult", "Riyan Parag", "Ravichandran Ashwin", "Shimron Hetmyer",
                  "Sandeep Sharma", "Kuldeep Sen", "Dhruv Jurel"]
    },
    "DC": {
        "full_name": "Delhi Capitals",
        "color": "#2561ae",
        "squad": ["Rishabh Pant", "Axar Patel", "Kuldeep Yadav", "Jake Fraser-McGurk",
                  "Tristan Stubbs", "Khaleel Ahmed", "David Warner", "Prithvi Shaw",
                  "Mitchell Marsh", "Anrich Nortje", "Mukesh Kumar"]
    },
    "PBKS": {
        "full_name": "Punjab Kings",
        "color": "#d71920",
        "squad": ["Sam Curran", "Arshdeep Singh", "Shashank Singh", "Kagiso Rabada",
                  "Jonny Bairstow", "Ashutosh Sharma", "Harshal Patel", "Liam Livingstone",
                  "Rilee Rossouw", "Atharva Taide", "Harpreet Brar"]
    },
    "LSG": {
        "full_name": "Lucknow Super Giants",
        "color": "#a4c639",
        "squad": ["KL Rahul", "Nicholas Pooran", "Marcus Stoinis", "Mayank Yadav",
                  "Ravi Bishnoi", "Quinton de Kock", "Krunal Pandya", "Deepak Hooda",
                  "Naveen-ul-Haq", "Mohsin Khan", "Amit Mishra"]
    },
    "GT": {
        "full_name": "Gujarat Titans",
        "color": "#1c1c1c",
        "squad": ["Shubman Gill", "Rashid Khan", "Sai Sudharsan", "David Miller",
                  "Mohammed Shami", "Rahul Tewatia", "Mohit Sharma", "Kane Williamson",
                  "Joshua Little", "Noor Ahmad", "Wriddhiman Saha"]
    }
}

# Pick random live match
team_keys = list(IPL_TEAMS.keys())
bat_key = random.choice(team_keys)
team_keys.remove(bat_key)
bowl_key = random.choice(team_keys)

bat_squad = IPL_TEAMS[bat_key]["squad"]
bowl_squad = IPL_TEAMS[bowl_key]["squad"]
b1 = random.choice(bat_squad)
b2 = random.choice([p for p in bat_squad if p != b1])
bwl = random.choice(bowl_squad)

score_data = {
    "batting_team": bat_key,
    "batting_full": IPL_TEAMS[bat_key]["full_name"],
    "bowling_team": bowl_key,
    "bowling_full": IPL_TEAMS[bowl_key]["full_name"],
    "runs": random.randint(100, 165),
    "wickets": random.randint(2, 5),
    "overs": random.randint(12, 16),
    "balls": random.randint(0, 5),
    "target": random.randint(180, 220),
    "batsman1": f"{b1} {random.randint(20,70)}*({random.randint(15,40)})",
    "batsman2": f"{b2} {random.randint(5,30)}*({random.randint(5,18)})",
    "bowler": f"{bwl} {random.randint(1,3)}-{random.randint(18,38)} ({random.randint(2,3)}.{random.randint(0,5)})",
    "last_event": "Match in Progress"
}

def simulate_score():
    global current_hype
    score_data["balls"] += 1
    if score_data["balls"] == 6:
        score_data["balls"] = 0
        score_data["overs"] += 1

    outcome = random.choice([0, 0, 1, 1, 2, 4, 6, "W"])
    if outcome == "W":
        score_data["wickets"] = min(10, score_data["wickets"] + 1)
        new_bat = random.choice(IPL_TEAMS[score_data["batting_team"]]["squad"])
        score_data["batsman1"] = f"{new_bat} 0*(0)"
        score_data["last_event"] = f"WICKET! {new_bat} comes in 🔴"
        current_hype = min(100, current_hype + 20)
    elif outcome == 6:
        score_data["runs"] += 6
        score_data["last_event"] = "SIX! 🚀 Ball in the stands!"
        current_hype = min(100, current_hype + 15)
    elif outcome == 4:
        score_data["runs"] += 4
        score_data["last_event"] = "FOUR! 💥 Racing to the boundary!"
        current_hype = min(100, current_hype + 8)
    else:
        score_data["runs"] += outcome
        score_data["last_event"] = f"{outcome} run{'s' if outcome != 1 else ''} taken"

def get_squad_context(team_name):
    for key, data in IPL_TEAMS.items():
        if key.lower() in team_name.lower() or team_name.lower() in key.lower() or team_name.lower() in data["full_name"].lower():
            return f"The {data['full_name']} ({key}) squad: {', '.join(data['squad'][:7])}."
    return f"An IPL team. Live match: {IPL_TEAMS[bat_key]['full_name']} vs {IPL_TEAMS[bowl_key]['full_name']}."

def update_sentiment(message):
    """Rough keyword-based sentiment update for speed"""
    global sentiment_breakdown
    msg = message.lower()
    if any(w in msg for w in ["six", "four", "boundary", "yes", "🔥", "🎉", "amazing", "great", "love"]):
        sentiment_breakdown["hype"] = min(100, sentiment_breakdown["hype"] + 8)
        sentiment_breakdown["happy"] = min(100, sentiment_breakdown["happy"] + 5)
    if any(w in msg for w in ["no", "out", "wicket", "😱", "worried", "nervous", "scared"]):
        sentiment_breakdown["nervous"] = min(100, sentiment_breakdown["nervous"] + 8)
    if any(w in msg for w in ["terrible", "bad", "hate", "worst", "angry", "stupid"]):
        sentiment_breakdown["angry"] = min(100, sentiment_breakdown["angry"] + 6)
    # Normalize
    total = sum(sentiment_breakdown.values())
    if total > 0:
        for k in sentiment_breakdown:
            sentiment_breakdown[k] = round(sentiment_breakdown[k] * 100 / total)

# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.route("/")
def index():
    return render_template('index.html', ipl_teams=list(IPL_TEAMS.keys()), team_data=IPL_TEAMS)

@app.route("/chat", methods=["POST"])
def chat():
    global current_hype, msg_id_counter, connected_fans
    data = request.json
    user_msg = data.get("message", "")
    team = data.get("team", "their team")
    sender = data.get("sender", "Fan")
    color = data.get("color", "#4facfe")

    update_sentiment(user_msg)
    simulate_score()
    connected_fans = max(50, connected_fans + random.randint(-3, 5))

    msg_id_counter += 1
    chat_messages.append({"id": msg_id_counter, "type": "user", "text": user_msg, "sender": sender, "color": color})

    ctx = get_squad_context(team)
    prompt = f"""
You are "HYPE BOT" - the ultimate energetic AI hype man for an IPL T20 live chat.
Live match: {score_data['batting_full']} {score_data['runs']}/{score_data['wickets']} in {score_data['overs']}.{score_data['balls']} overs (Target: {score_data['target']}).
Last event: {score_data['last_event']}.
{ctx}
Crowd hype: {current_hype}/100.
Fan "{sender}" supporting {team} said: "{user_msg}"

Reply rules:
- Be WILDLY energetic, funny, and use cricket slang + IPL-specific references
- 1-2 sentences MAX. Use emojis freely.
- Reference actual player names if relevant
- Assign hype 1-100

Output EXACTLY:
HYPE: [number]
REPLY: [message]
"""

    reply_text = f"LESSS GOOOO {sender}! 🏏🔥 The IPL never sleeps!"
    if client:
        try:
            raw = generate(prompt)
            for line in raw.split('\n'):
                if line.upper().startswith("HYPE:"):
                    try: current_hype = max(10, min(100, int(''.join(filter(str.isdigit, line.split(':',1)[1])))))
                    except: pass
                elif line.upper().startswith("REPLY:"):
                    reply_text = line.split(':', 1)[1].strip()
        except Exception as e:
            print(f"[Gemini /chat error] {e}")
            reply_text = f"Stump mic is down! 🎤 But the vibe is IMMACULATE! 🔥"

    msg_id_counter += 1
    chat_messages.append({"id": msg_id_counter, "type": "bot", "text": reply_text, "sender": "HYPE BOT", "color": "#f093fb"})
    return jsonify({"success": True})

@app.route("/action", methods=["POST"])
def action():
    global current_hype, msg_id_counter
    data = request.json
    action_type = data.get("action", "")
    team = data.get("team", "the team")
    ctx = get_squad_context(team)

    prompts_map = {
        "roast": f"""Roast the opponents of {team} in this IPL match in a HILARIOUS, over-the-top but friendly way. 
                     {ctx}. Reference specific players by name! 2 sentences max. Pure savage comedy. Use emojis.""",
        "cheer": f"""Create an electric, catchy 2-line stadium chant for {team} right now in an IPL game! 
                     {ctx} ALL CAPS! Make it rhyme if possible. Include team-specific player names. Use emojis.""",
        "reaction": f"""A WILD cricket moment just happened in the IPL! (Imagine a stunning catch, a helicopter shot 6, or a hat-trick ball.) 
                       React as an INSANELY enthusiastic hype man in 1-2 sentences. ALL CAPS. Pure excitement. Emojis overload!""",
        "meme": f"""The IPL match is super tense right now for {team}. {ctx}
                    Describe a GENIUS, funny internet meme that perfectly captures this moment. 
                    Format: "TOP TEXT / [image description] / BOTTOM TEXT". Be creative and specific to IPL! 2-3 sentences.""",
        "sentiment": f"""Based on a cricket chat where hype={current_hype}/100, 
                         give a funny 1-sentence crowd mood report right now for an IPL match involving {team}. Use emojis."""
    }

    hype_boosts = {"roast": 15, "cheer": 22, "reaction": 40, "meme": 12, "sentiment": 5}
    prompt = prompts_map.get(action_type, "Yell something hype about IPL!")

    simulate_score()
    reply_text = f"*Legendary {action_type} energy for {team}!* (Set your API key to unlock real AI magic 🔮)"

    if client:
        try:
            reply_text = generate(prompt)
        except Exception as e:
            print(f"[Gemini /action error] {e}")
            reply_text = "Something went sideways on the pitch! 😅 Try again!"

    current_hype = min(100, current_hype + hype_boosts.get(action_type, 10))
    msg_id_counter += 1
    
    icon_map = {"roast":"🔥", "cheer":"🙌", "reaction":"😱", "meme":"😂", "sentiment":"📊"}
    label_map = {"roast":"SAVAGE ROAST", "cheer":"STADIUM CHANT", "reaction":"WILD REACTION", "meme":"MEME DROP", "sentiment":"CROWD VIBE CHECK"}
    
    chat_messages.append({
        "id": msg_id_counter, "type": "action",
        "text": reply_text, "sender": f"{icon_map.get(action_type,'🤖')} {label_map.get(action_type,'HYPE BOT')}",
        "color": "#f093fb", "action_type": action_type
    })
    return jsonify({"success": True})

@app.route("/trivia", methods=["GET"])
def trivia():
    global msg_id_counter
    team = request.args.get("team", "IPL")
    ctx = get_squad_context(team)
    prompt = f"""Generate a fun IPL trivia question about {team} or IPL history in general. {ctx}
Return ONLY valid JSON:
{{"question":"...","options":["A","B","C","D"],"answer":"exact matching option text","fun_fact":"1 interesting sentence about the answer"}}"""

    widget_data = {
        "question": "Which team won the first-ever IPL title in 2008?",
        "options": ["CSK", "Rajasthan Royals", "MI", "RCB"],
        "answer": "Rajasthan Royals",
        "fun_fact": "Rajasthan Royals beat Chennai Super Kings in the 2008 IPL Final!",
        "is_trivia": True
    }
    if client:
        try:
            text = generate(prompt)
            if "```" in text: text = text.split("```")[1].replace("json","").strip()
            parsed = json.loads(text)
            parsed["is_trivia"] = True
            widget_data = parsed
        except Exception as e:
            print(f"[Gemini /trivia error] {e}")

    msg_id_counter += 1
    chat_messages.append({"id": msg_id_counter, "type": "widget", "data": widget_data, "sender": "🧠 TRIVIA BOT", "color": "#a78bfa"})
    return jsonify({"success": True})

@app.route("/poll", methods=["GET"])
def poll():
    global msg_id_counter
    team = request.args.get("team", "IPL")
    ctx = get_squad_context(team)
    prompt = f"""Generate an exciting, real-time IPL fan poll for {team}. {ctx}
Make it very specific to the current squad. Return ONLY valid JSON:
{{"question":"...","options":["opt1","opt2","opt3","opt4"]}}"""

    widget_data = {"question": f"Who will win the match?", "options": [IPL_TEAMS[bat_key]["full_name"], IPL_TEAMS[bowl_key]["full_name"], "Super Over! 🤯", "Rain interruption 🌧️"], "is_poll": True}
    if client:
        try:
            text = generate(prompt)
            if "```" in text: text = text.split("```")[1].replace("json","").strip()
            parsed = json.loads(text)
            parsed["is_poll"] = True
            widget_data = parsed
        except Exception as e:
            print(f"[Gemini /poll error] {e}")

    msg_id_counter += 1
    chat_messages.append({"id": msg_id_counter, "type": "widget", "data": widget_data, "sender": "📊 POLL BOT", "color": "#34d399"})
    return jsonify({"success": True})

# ── Crowd Reaction Aggregator ──
reaction_counts = {}          # per-emoji totals (for individual throttle)
crowd_reaction_buffer = []    # rolling window of recent reactions
CROWD_TRIGGER = 8             # fire a mutual reaction every N reactions

def build_mutual_reaction(buffer, senders):
    """Build a crowd pulse summary from the reaction buffer."""
    from collections import Counter
    tally = Counter(buffer)
    total = len(buffer)
    top = tally.most_common(3)

    # Build a text breakdown e.g. "🔥×5, 😱×2, 👏×1"
    breakdown = "  ".join(f"{e}×{c}" for e, c in top)
    dominant_emoji, dominant_count = top[0]
    pct = round(dominant_count / total * 100)

    # Mood label
    mood_map = {
        "🔥": ("ON FIRE", "The crowd is BURNING with energy!"),
        "😱": ("SHOCKED", "Everyone is absolutely STUNNED!"),
        "🏏": ("CRICKET MAD", "Pure cricket passion in the house!"),
        "👏": ("RESPECTFUL", "Class appreciation from the stands!"),
        "💔": ("HEARTBROKEN", "The sadness is REAL right now...")
    }
    mood_label, mood_desc = mood_map.get(dominant_emoji, ("HYPED", "The crowd is going WILD!"))

    fallback = (
        f"🌊 CROWD PULSE — {breakdown}\n"
        f"{pct}% of fans are {dominant_emoji} right now!\n"
        f"Mood: **{mood_label}** — {mood_desc} 🏟️"
    )

    if client:
        try:
            prompt = f"""You are an IPL hype man bot. The last {total} fan reactions were:
{breakdown}
The dominant mood is {dominant_emoji} ({pct}% of fans).
Match: {score_data['batting_team']} {score_data['runs']}/{score_data['wickets']} in {score_data['overs']}.{score_data['balls']} overs.

Write a 2-sentence CROWD PULSE announcement that:
1. Summarizes what ALL fans are feeling together as one crowd
2. Reacts to this collective energy with epic IPL hype

Start with '🌊 CROWD PULSE —' and use emojis freely."""
            return generate(prompt)
        except Exception:
            pass
    return fallback


@app.route("/react", methods=["POST"])
def react():
    global current_hype, msg_id_counter, reaction_id_counter
    data = request.json
    emoji = data.get("emoji", "❤️")
    sender = data.get("sender", "A fan")

    # Count reactions per emoji for throttling
    reaction_counts[emoji] = reaction_counts.get(emoji, 0) + 1

    # Agent reacts automatically to every 3rd reaction of the same emoji
    # This prevents spam but keeps it lively
    if reaction_counts[emoji] % 3 == 0:
        # Smart pre-built fallbacks (no API needed)
        fallbacks = {
            "🔥": [
                f"THE STADIUM IS ON FIRE!! 🔥🔥 {sender} just poured kerosene on the vibe!!",
                f"🔥 PURE FLAMES from {sender}! IPL energy is UNMATCHED today!",
                f"That 🔥 from {sender} broke the hype meter! WE ARE COOKING! 🏏"
            ],
            "🏏": [
                f"🏏 {sender} knows cricket! This shot is going to be LEGENDARY!",
                f"CRICKET CRAZY alert! 🏏 {sender} living for the game rn!",
                f"🏏🏏 The bat is talking and {sender} is LISTENING! LET'S GOOO!"
            ],
            "😱": [
                f"😱 EVEN {sender} can't believe what just happened!! UNREAL moment!",
                f"THE SHOCK IS REAL!! 😱 {sender} is shook and honestly SAME!",
                f"😱😱 {sender} has left the chat mentally! This IPL moment is INSANE!"
            ],
            "👏": [
                f"👏 {sender} showing RESPECT! That's what class looks like on the pitch!",
                f"STANDING OVATION from {sender}! 👏 Absolutely brilliant cricket!",
                f"👏 Well deserved! Even {sender} agrees — that was SPECIAL! 🏏"
            ],
            "💔": [
                f"💔 We feel you {sender}... but the match isn't over yet! BELIEVE!",
                f"Ouch 💔 That hurts! But {sender}, we NEVER give up in the IPL!!",
                f"💔 Heartbreak hotel for {sender}... but a comeback is coming! 👀🏏"
            ]
        }

        # Try Gemini first, fall back to pre-built response
        bot_reply = random.choice(fallbacks.get(emoji, [f"The crowd goes WILD after {sender}'s {emoji}! INCREDIBLE energy! 🏏🔥"]))

        if client:
            try:
                prompt = f"""You are an IPL hype man bot in a live cricket chat. 
A fan named '{sender}' just sent the reaction emoji '{emoji}'.
The current match score: {score_data['batting_team']} {score_data['runs']}/{score_data['wickets']} in {score_data['overs']}.{score_data['balls']} overs.
Respond with ONE short, high-energy reaction to their emoji (1 sentence, max 15 words). Use emojis. Be funny and cricket-specific."""
                bot_reply = generate(prompt)
            except Exception:
                pass  # Use fallback

        current_hype = min(100, current_hype + 5)
        msg_id_counter += 1
        chat_messages.append({
            "id": msg_id_counter,
            "type": "bot",
            "text": bot_reply,
            "sender": "HYPE BOT",
            "color": "#f093fb"
        })

    # Always broadcast the emoji to all fans
    reaction_id_counter += 1
    reactions_log.append({"id": reaction_id_counter, "emoji": emoji})
    if len(reactions_log) > 200:
        reactions_log.pop(0)

    # ── Crowd Reaction Buffer (Mutual Reaction) ──
    crowd_reaction_buffer.append(emoji)
    # Keep a rolling window of last 30 reactions max
    if len(crowd_reaction_buffer) > 30:
        crowd_reaction_buffer.pop(0)

    # Every CROWD_TRIGGER reactions → fire one mutual crowd pulse
    total_count = sum(reaction_counts.values())
    if total_count % CROWD_TRIGGER == 0 and total_count > 0:
        mutual_text = build_mutual_reaction(list(crowd_reaction_buffer), sender)
        current_hype = min(100, current_hype + 12)
        msg_id_counter += 1
        chat_messages.append({
            "id": msg_id_counter,
            "type": "action",
            "text": mutual_text,
            "sender": "🌊 CROWD PULSE",
            "color": "#34d399",
            "action_type": "sentiment"
        })

    return jsonify({"success": True})

@app.route("/sync", methods=["GET"])
def sync():
    global current_hype, connected_fans
    last_id = int(request.args.get("last_id", 0))
    last_reaction_id = int(request.args.get("last_reaction_id", 0))
    current_hype = max(10, current_hype - 0.4)
    connected_fans = max(50, connected_fans + random.randint(-2, 3))

    if random.random() < 0.25:
        simulate_score()

    new_msgs = [m for m in chat_messages if m["id"] > last_id]
    # Each client gets only reactions it hasn't seen yet — no clearing!
    new_reactions = [r for r in reactions_log if r["id"] > last_reaction_id]

    return jsonify({
        "hype_level": int(current_hype),
        "sentiment": sentiment_breakdown,
        "messages": new_msgs,
        "reactions": [r["emoji"] for r in new_reactions],
        "last_reaction_id": reactions_log[-1]["id"] if reactions_log else 0,
        "score": score_data,
        "connected_fans": connected_fans
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
