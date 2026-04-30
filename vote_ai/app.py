import os
import random
import string
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import errors

app = Flask(__name__)

# Try initializing API key, handle securely
api_key = os.getenv("GEMINI_API_KEY")
try:
    client = genai.Client(api_key=api_key) if api_key else None
except Exception as e:
    client = None
    print(f"GenAI Client Init Error: {e}")

def ai_response(query, lang="English"):
    # Fallback mechanism if API key is invalid or not set
    if not client:
        return _fallback_response(query)

    prompt = f"""
    You are VoteGuide AI, an expert, friendly Election Assistant.
    
    Guidelines:
    1. Answer clearly and concisely in simple language.
    2. Use bullet points and emojis to make the response engaging.
    3. If the user asks about election procedures, guide them step-by-step.
    3. If the user asks about election procedures, guide them step-by-step.
    4. Stay neutral and strictly informative.
    5. CRITICAL: You MUST respond strictly in the language: {lang}.
    
    User Query: {query}
    """

    try:
        res = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return res.text if res.text else "Sorry, I couldn't generate a response."
    except errors.APIError as e:
        print(f"Gemini API Error: {e}")
        return "⚠️ I'm currently running in offline mode. " + _fallback_response(query)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return "⚠️ I'm currently running in offline mode. " + _fallback_response(query)

def _fallback_response(query):
    """Provides mock responses when AI is down to keep the app functional."""
    query = query.lower()
    if "vote" in query or "how" in query:
        return "🗳️ **How to Vote:**<br>1. Register for a Voter ID.<br>2. Check your name in the electoral roll.<br>3. Find your polling booth.<br>4. Carry a valid ID and cast your vote!"
    elif "process" in query or "election" in query:
        return "🏛️ **Election Process:**<br>Elections involve voter registration, candidate nomination, campaigning, voting day, and finally, counting of votes to declare the winner."
    else:
        return "🤖 **Offline Mode Active:**<br>I'm currently unable to connect to my AI brain. But you can still use the **Step Guide** and **Check Eligibility** buttons on the left!"

# 🗳️ GUIDE DATA
STEPS_DATA = [
    "✅ Check eligibility (18+ citizen)",
    "📝 Register for Voter ID card (Form 6)",
    "🔍 Verify your details on the electoral roll",
    "📍 Find your designated polling booth",
    "🆔 Carry a valid ID proof on election day",
    "🗳️ Cast your vote on the EVM/Ballot",
    "📊 Wait for the election results"
]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/ask")
def ask():
    q = request.args.get("q")
    lang = request.args.get("lang", "English")
    if not q:
        return jsonify({"message": "Please ask a question."})
    response_text = ai_response(q, lang)
    # Convert newlines to HTML breaks for better UI formatting if not already formatted
    if "<br>" not in response_text and "<ul>" not in response_text:
        response_text = response_text.replace("\n", "<br>")
        
    return jsonify({"message": response_text})

@app.route("/guide")
def guide():
    return jsonify({"steps": STEPS_DATA})

@app.route("/check")
def check():
    try:
        age = int(request.args.get("age", 0))
        if age >= 18:
            return jsonify({
                "eligible": True, 
                "result": f"Awesome! At {age} years old, you are **eligible** to vote. Make sure you register for your Voter ID!"
            })
        else:
            return jsonify({
                "eligible": False, 
                "result": f"You are {age} years old. You must be **18 or older** to vote. You can register once you turn 18!"
            })
    except ValueError:
        return jsonify({"eligible": False, "result": "Invalid age provided."})

def generate_voter_id():
    state = "MH"
    year = "2026"
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{state}-{year}-{rand}"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    name = data.get("name", "").strip()
    age_str = data.get("age", "")
    address = data.get("address", "").strip()

    errors = []
    if not name:
        errors.append("Name is missing")
    if not address:
        errors.append("Address is missing")
    
    try:
        age = int(age_str)
        if age < 18:
            errors.append(f"Age must be 18+. You are {age}.")
    except ValueError:
        errors.append("Valid age is required")

    if errors:
        return jsonify({
            "success": False,
            "message": f"""
            ⚠️ <b>Your data is incomplete or invalid:</b><br>
            → {"<br>→ ".join(errors)}<br><br>
            
            <b>Steps to correct info:</b><br>
            1. Ensure your age is 18 or above.<br>
            2. Provide your complete residential address.<br><br>
            
            <b>📝 Document Checklist for Registration:</b><br>
            - Proof of Identity (Aadhar/PAN/Passport)<br>
            - Proof of Address (Utility Bill/Rent Agreement)<br>
            - Passport Size Photograph<br><br>
            
            <b>🏢 Nearest Registration Office:</b><br>
            Mock Electoral Office, Downtown District-12
            """
        })

    voter_id = generate_voter_id()
    return jsonify({
        "success": True,
        "message": f"✅ <b>Voter ID Generated Successfully</b><br><br><b>Name:</b> {name}<br><b>Voter ID:</b> {voter_id}<br><b>Booth:</b> District-12<br><b>Status:</b> Active<br><br><b>📝 What to carry on Election Day:</b><br>- Printout of this Voter ID<br>- Original Aadhar Card/PAN<br><br><small><i>Note: This system simulates voter ID generation for educational purposes.</i></small>"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, threaded=True)
