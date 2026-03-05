# ════════════════════════════════════════
#  MUMMUM WHATSAPP AI BOT
#  Built with Twilio + Claude AI
#  By Prasad — Maya Media Works
# ════════════════════════════════════════

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import anthropic
import os

app = Flask(__name__)

# ── Your Claude AI client ──
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# ── Conversation memory (per customer) ──
conversations = {}

# ── MumMum Bot Brain ──
SYSTEM_PROMPT = """You are MumMum's official WhatsApp AI 
assistant. MumMum is a millet-based instant drink kiosk 
brand in Coimbatore, Tamil Nadu. 
Tagline: Ancient Grains. Modern Sips.

MENU — All drinks Rs.40:
1. Nuts Ragi Kanji — Malted Ragi + Dry Fruits — Hot
2. Verkadalai Kambu Koolu — Malted Kambu + Peanut — Hot
3. Ulunthu Vellam Sip — Black Urad Dal + Jaggery — Hot
4. Thinai Thenum — Malted Thinai + Dates + Honey — Hot/Cold
5. Cocoa Kuthiraivali — Malted Kuthiraivali + Cocoa — Hot/Cold

LOCATIONS:
- GH Hospital, RS Puram
- PSG College, Peelamedu
- Brookefields Mall
- Railway Station, Junction
All open 7AM to 9PM daily.

HEALTH GUIDE:
- Diabetes → Thinai Thenum (low glycemic)
- Weight loss → Cocoa Kuthiraivali (high fiber)
- Pregnancy/Iron → Ulunthu Vellam Sip (iron rich)
- Children/Calcium → Nuts Ragi Kanji (high calcium)
- Heart/BP → Verkadalai Kambu Koolu (heart healthy)

FRANCHISE:
- Zero royalty model
- Setup cost Rs.1.2 lakhs per kiosk
- Break even 73 cups per day
- Monthly profit Rs.25,000+
- Powder supplied by MumMum central kitchen

RULES:
- Keep replies short — max 8 lines for WhatsApp
- Use *bold* for important words
- Use emojis naturally
- For complaints: apologize + offer 1 free cup
- For Tamil messages: reply in Tamil
- Always end with a helpful question
- Sign off with MumMum brand voice"""


@app.route("/bot", methods=["POST"])
def bot():
    # Get customer message
    incoming = request.values.get("Body", "").strip()
    customer_number = request.values.get("From", "")

    # Remember conversation per customer
    if customer_number not in conversations:
        conversations[customer_number] = []

    # Add customer message to history
    conversations[customer_number].append({
        "role": "user",
        "content": incoming
    })

    # Keep only last 10 messages (memory limit)
    if len(conversations[customer_number]) > 10:
        conversations[customer_number] = \
            conversations[customer_number][-10:]

    try:
        # Ask Claude AI for reply
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=conversations[customer_number]
        )

        bot_reply = response.content[0].text

        # Save bot reply to memory
        conversations[customer_number].append({
            "role": "assistant",
            "content": bot_reply
        })

    except Exception as e:
        # Fallback if API fails
        bot_reply = (
            "Vanakkam! I am MumMum assistant. "
            "Reply MENU to see our drinks, "
            "LOCATION for kiosk addresses, "
            "or HEALTH for recommendations. "
            "All drinks Rs.40 only! "
        )

    # Send reply via Twilio
    resp = MessagingResponse()
    resp.message(bot_reply)
    return str(resp)


@app.route("/", methods=["GET"])
def home():
    return "MumMum WhatsApp Bot is LIVE! "


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

---

### Create a file called `requirements.txt`
```
flask
twilio
anthropic
gunicorn
```

---

## 📋 PHASE 4 — DEPLOY TO RAILWAY
### Time: 15 minutes | Cost: Rs. 0

| Step | Action |
|------|--------|
| **1** | Go to **railway.app** — login |
| **2** | Click **"New Project"** |
| **3** | Click **"Deploy from GitHub"** |
| **4** | Upload your 2 files (app.py + requirements.txt) |
| **5** | Click **"Variables"** — add these: |
```
ANTHROPIC_API_KEY = your_claude_key_here
