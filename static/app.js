// static/app.js - IPL Hype Hub Client Logic

let myName = "Fan", myTeam = "IPL", myColor = "#ffcc00";
let lastId = 0, lastReactionId = 0, polling = false;

// Unique ID per browser tab — used by server to count real fans
const sessionId = Math.random().toString(36).slice(2) + Date.now().toString(36);

const feed = document.getElementById('feed');
const hypeFill = document.getElementById('hypeFill');
const hypePct = document.getElementById('hypePct');
const liveCount = document.getElementById('liveCount');

// Auto-restore saved name so fans don’t re-type after refresh
const _saved = localStorage.getItem('ipl_fan_name');
if (_saved) document.getElementById('fanName').value = _saved;

// Allow Enter key on login screen
document.getElementById('fanName').addEventListener('keypress', e => {
  if (e.key === 'Enter') startApp();
});

// ── Team data for color theming ──
const TEAM_COLORS = {
  CSK:"#f5a623", MI:"#004c93", RCB:"#c8102e", KKR:"#3a225d",
  SRH:"#f26522", RR:"#e83283", DC:"#2561ae", PBKS:"#d71920",
  LSG:"#a4c639", GT:"#b5a642"
};

window.startApp = function() {
  const n = document.getElementById('fanName').value.trim();
  if (!n) { document.getElementById('fanName').focus(); return; }
  myName = n;
  localStorage.setItem('ipl_fan_name', myName); // remember name across refreshes
  document.getElementById('overlay').style.display = 'none';
  fetch('/chat', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({message:`${myName} just joined the stadium! LET'S GOOOO! 🏏`, team:'IPL', sender:myName, color:myColor})
  });
  polling = true;
  sync();
};

// ── Hype Visuals ──
function setHype(lvl) {
  hypeFill.style.height = lvl + '%';
  hypePct.textContent = lvl + '%';
  lvl >= 95 ? hypeFill.classList.add('max') : hypeFill.classList.remove('max');
}

// ── Sentiment bars ──
function setSentiment(s) {
  const total = (s.hype||0)+(s.happy||0)+(s.nervous||0)+(s.angry||0) || 1;
  document.getElementById('sHype').style.width    = (s.hype/total*100)+'%';
  document.getElementById('sHappy').style.width   = (s.happy/total*100)+'%';
  document.getElementById('sNervous').style.width = (s.nervous/total*100)+'%';
  document.getElementById('sAngry').style.width   = (s.angry/total*100)+'%';
  document.getElementById('sentimentText').textContent =
    `🔥 ${s.hype}%  😊 ${s.happy}%  😬 ${s.nervous}%  😤 ${s.angry}%`;
}

// ── Scoreboard ──
function setScore(sc) {
  document.getElementById('batTeam').textContent   = sc.batting_team;
  document.getElementById('bowlTeam').textContent  = sc.bowling_team;
  document.getElementById('runsWick').textContent  = `${sc.runs}/${sc.wickets}`;
  document.getElementById('overs').textContent     = `(${sc.overs}.${sc.balls})`;
  document.getElementById('target').textContent    = `Target: ${sc.target}`;
  document.getElementById('bat1').textContent      = sc.batsman1;
  document.getElementById('bat2').textContent      = sc.batsman2;
  document.getElementById('bowler').textContent    = sc.bowler;
  document.getElementById('lastEvt').textContent   = sc.last_event;
}

// ── Message rendering ──
function addMsg(text, cls, name, nameColor, extraClass='') {
  const w = document.createElement('div');
  w.className = `msg ${cls} ${extraClass}`;
  if (cls !== 'system') {
    const nm = document.createElement('div');
    nm.className = 'msg-name';
    nm.style.color = nameColor || (cls==='me' ? myColor : '#a78bfa');
    nm.textContent = name || (cls==='me' ? myName : 'HYPE BOT');
    w.appendChild(nm);
  }
  const b = document.createElement('div');
  b.className = 'bubble';
  b.innerHTML = (text||'').replace(/\n/g,'<br>');
  w.appendChild(b);
  feed.appendChild(w);
  feed.scrollTop = feed.scrollHeight;
  if (cls === 'bot' || cls === 'action') triggerShake();
}

function addWidget(data, color) {
  const w = document.createElement('div');
  w.className = 'msg bot';
  const nm = document.createElement('div');
  nm.className = 'msg-name'; nm.style.color = color;
  nm.textContent = data.is_trivia ? '🧠 TRIVIA BOT' : '📊 POLL BOT';
  w.appendChild(nm);
  const card = document.createElement('div');
  card.className = `widget-card ${data.is_trivia ? 'trivia' : 'poll'}`;
  const head = document.createElement('div'); head.className = 'widget-head';
  head.textContent = data.is_trivia ? '⚡ LIVE TRIVIA' : '📊 LIVE POLL';
  card.appendChild(head);
  const q = document.createElement('div'); q.className = 'widget-q'; q.textContent = data.question;
  card.appendChild(q);
  const opts = document.createElement('div'); opts.className = 'widget-opts';
  (data.options||[]).forEach(opt => {
    const btn = document.createElement('button'); btn.className = 'w-opt'; btn.textContent = opt;
    if (data.is_trivia) {
      btn.onclick = () => {
        if (opts.dataset.done) return; opts.dataset.done = '1';
        Array.from(opts.children).forEach(b => {
          b.classList.add(b.textContent === data.answer ? 'correct' : (b === btn ? 'wrong' : 'dimmed'));
        });
        if (data.fun_fact) {
          const ff = document.createElement('div'); ff.className='fun-fact'; ff.textContent='💡 '+data.fun_fact;
          card.appendChild(ff);
        }
        showEmoji('🧠');
      };
    } else {
      btn.onclick = () => {
        if (opts.dataset.done) return; opts.dataset.done = '1';
        const pct = Math.floor(Math.random()*30+35);
        btn.classList.add('voted');
        btn.textContent += ` — ${pct}%`;
        Array.from(opts.children).forEach(b => {
          if (b !== btn) { b.classList.add('dimmed'); b.textContent += ` — ${Math.floor(Math.random()*25+5)}%`; }
        });
        showEmoji('📊');
      };
    }
    opts.appendChild(btn);
  });
  card.appendChild(opts);
  w.appendChild(card);
  feed.appendChild(w);
  feed.scrollTop = feed.scrollHeight;
  triggerShake();
}

// ── Actions ──
window.triggerAction = function(type) {
  fetch('/action', { method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({action:type, team:myTeam})
  });
};
window.triggerPoll   = () => fetch(`/poll?team=${encodeURIComponent(myTeam)}`);
window.triggerTrivia = () => fetch(`/trivia?team=${encodeURIComponent(myTeam)}`);


// ── Reactions ──
window.sendReaction = function(emoji) {
  showEmoji(emoji);
  fetch('/react', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ emoji: emoji, sender: myName })
  });
};
function showEmoji(emoji) {
  const c = document.getElementById('fx');
  const el = document.createElement('div'); el.className='fx-e'; el.textContent=emoji;
  el.style.setProperty('--dx', (Math.random()-.5)*130+'px');
  c.appendChild(el); setTimeout(()=>el.remove(), 2500);
}

// ── Shake ──
function triggerShake() {
  document.body.classList.remove('shake'); void document.body.offsetWidth;
  document.body.classList.add('shake');
}

// ── Sync polling ──
async function sync() {
  if (!polling) return;
  try {
    const r = await fetch(`/sync?last_id=${lastId}&last_reaction_id=${lastReactionId}&sid=${sessionId}&fan=${encodeURIComponent(myName)}`);
    const d = await r.json();
    setHype(d.hype_level);
    if (d.sentiment) setSentiment(d.sentiment);
    if (d.score) setScore(d.score);
    if (d.connected_fans !== undefined) liveCount.textContent = d.connected_fans;
    // Update our reaction cursor — never re-show old reactions
    if (typeof d.last_reaction_id !== 'undefined') lastReactionId = d.last_reaction_id;
    (d.messages||[]).forEach(m => {
      if (m.id <= lastId) return;
      lastId = m.id;
      if (m.type==='widget') addWidget(m.data, m.color);
      else if (m.type==='action') addMsg(m.text, 'action', m.sender, m.color, m.action_type||'');
      else if (m.type==='user') addMsg(m.text, 'me', m.sender, m.color);
      else addMsg(m.text, 'bot', m.sender, m.color);
    });
    (d.reactions||[]).forEach(showEmoji);
  } catch(e) {}
  setTimeout(sync, 1500);
}
