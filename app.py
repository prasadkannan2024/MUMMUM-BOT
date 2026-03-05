from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import anthropic
import os

app = Flask(__name__)
conversations = {}

SYSTEM_PROMPT = """You are MumMum's official WhatsApp AI assistant.
MumMum is a millet-based instant drink kiosk brand in Coimbatore,
Tamil Nadu. Tagline: Ancient Grains. Modern Sips.

MENU - All drinks Rs.40:
1. Nuts Ragi Kanji - Malted Ragi and Dry Fruits - Hot
2. Verkadalai Kambu Koolu - Malted Kambu and Peanut - Hot
3. Ulunthu Vellam Sip - Black Urad Dal and Jaggery - Hot
4. Thinai Thenum - Malted Thinai and Dates and Honey - Hot or Cold
5. Cocoa Kuthiraivali - Malted Kuthiraivali and Cocoa - Hot or Cold

LOCATIONS:
- GH Hospital RS Puram
- PSG College Peelamedu
- Brookefields Mall
- Railway Station Junction
All open 7AM to 9PM daily.

HEALTH GUIDE:
- Diabetes: Thinai Thenum low glycemic index
- Weight loss: Cocoa Kuthiraivali high fiber
- Pregnancy or Iron: Ulunthu Vellam Sip iron rich
- Children or Calcium: Nuts Ragi Kanji high calcium
- Heart or BP: Verkadalai Kambu Koolu heart healthy

FRANCHISE INFO:
- Zero royalty model
- Setup cost Rs.1.2 lakhs per kiosk
- Break even 73 cups per day
- Monthly profit Rs.25000 and above
- Full training and powder supply provided

RULES:
- Keep replies short, max 8 lines for WhatsApp
- Use *bold* for important words
- Use emojis naturally
- For complaints: apologize and offer 1 free cup
- For Tamil messages: reply in Tamil
- Always end with a helpful question
- Be warm and friendly
- If customer types MENU or menu or drinks or list, always show all 5 drinks with prices clearly
- Never repeat the welcome message again after the first message
- Give different helpful responses each time based on what customer asks"""


WELCOME_MESSAGE = """🌾 *Vanakkam! Welcome to MumMum!* ☕

*Ancient Grains. Modern Sips.*

I am your MumMum assistant! Here is what I can help with:

🥤 Type *MENU* - See all 5 millet drinks
📍 Type *LOCATION* - Find nearest kiosk
💚 Type *HEALTH* - Get drink recommendation
🏪 Type *FRANCHISE* - Business opportunity

All drinks just *Rs.40* only! 😊
What would you like to know?"""


MENU_MESSAGE = """🌾 *MumMum Drink Menu* - All at *Rs.40*

1️⃣ *Nuts Ragi Kanji* 🔥
   Malted Ragi + Dry Fruits | Hot

2️⃣ *Verkadalai Kambu Koolu* 🔥
   Malted Kambu + Peanut | Hot

3️⃣ *Ulunthu Vellam Sip* 🔥
   Black Urad Dal + Jaggery | Hot

4️⃣ *Thinai Thenum* 🔥❄️
   Malted Thinai + Dates + Honey | Hot or Cold

5️⃣ *Cocoa Kuthiraivali* 🔥❄️
   Malted Kuthiraivali + Cocoa | Hot or Cold

Which drink interests you? I can suggest based on your health needs too! 💚"""


LOCATION_MESSAGE = """📍 *MumMum Kiosk Locations*

1️⃣ GH Hospital - RS Puram
2️⃣ PSG College - Peelamedu
3️⃣ Brookefields Mall
4️⃣ Railway Station Junction

⏰ All open *7AM to 9PM* daily

Which location is nearest to you? 😊"""


HEALTH_MESSAGE = """💚 *MumMum Health Guide*

🩸 *Diabetes* → Thinai Thenum (low glycemic)
⚖️ *Weight Loss* → Cocoa Kuthiraivali (high fiber)
🤰 *Pregnancy/Iron* → Ulunthu Vellam Sip (iron rich)
👶 *Children/Calcium* → Nuts Ragi Kanji (high calcium)
❤️ *Heart/BP* → Verkadalai Kambu Koolu (heart healthy)

Tell me your health need and I will recommend the perfect drink! 😊"""


FRANCHISE_MESSAGE = """🏪 *MumMum Franchise Opportunity*

✅ *Zero royalty* model
💰 Setup cost: *Rs.1.2 lakhs* per kiosk
📈 Break even: *73 cups per day*
💵 Monthly profit: *Rs.25,000+*
🎓 Full training + powder supply provided

Interested in owning a MumMum kiosk? 
Reply *YES* and we will connect you with our team! 😊"""


@app.route("/bot", methods=["POST"])
def bot():
    incoming = request.values.get("Body", "").strip()
    customer = request.values.get("From", "unknown")
    incoming_lower = incoming.lower().strip()

    # Handle keyword commands directly without AI
    if incoming_lower in ["menu", "மெனு", "drinks", "list", "drink"]:
        reply = MENU_MESSAGE
        return str(MessagingResponse().message(reply))

    if incoming_lower in ["location", "locations", "where", "address", "இடம்"]:
        reply = LOCATION_MESSAGE
        return str(MessagingResponse().message(reply))

    if incoming_lower in ["health", "healthy", "suggest", "recommendation", "உடல்நலம்"]:
        reply = HEALTH_MESSAGE
        return str(MessagingResponse().message(reply))

    if incoming_lower in ["franchise", "business", "invest", "தொழில்"]:
        reply = FRANCHISE_MESSAGE
        return str(MessagingResponse().message(reply))

    # First message - send welcome
    if customer not in conversations or len(conversations[customer]) == 0:
        conversations[customer] = []
        reply = WELCOME_MESSAGE
        conversations[customer].append({"role": "user", "content": incoming})
        conversations[customer].append({"role": "assistant", "content": reply})
        return str(MessagingResponse().message(reply))

    # All other messages - use Claude AI
    conversations[customer].append({"role": "user", "content": incoming})

    if len(conversations[customer]) > 10:
        conversations[customer] = conversations[customer][-10:]

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("No API key found")

        ai_client = anthropic.Anthropic(api_key=api_key)
        response = ai_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=conversations[customer]
        )
        reply = response.content[0].text
        conversations[customer].append({"role": "assistant", "content": reply})

    except Exception as e:
        reply = (
            "Vanakkam! I am MumMum assistant. "
            "Reply *MENU* to see our drinks. "
            "All drinks Rs.40 only! "
            "Visit GH Hospital or PSG College kiosk. 🌾"
        )

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)


@app.route("/", methods=["GET"])
def home():
    return "MumMum WhatsApp Bot is LIVE! 🌾"


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "bot": "MumMum"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
