import os
import random
import string
import sqlite3
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

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT, category_id INTEGER, votes INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS voters (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, location TEXT)''')
    
    # Seed data only if empty
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO categories (name) VALUES ('Student Chairman')")
        c.execute("INSERT INTO categories (name) VALUES ('Student Vice-Chairman')")
        c.execute("INSERT INTO categories (name) VALUES ('Executive Members')")
        c.execute("INSERT INTO candidates (name, category_id) VALUES ('Kamal',1)")
        c.execute("INSERT INTO candidates (name, category_id) VALUES ('Rajni',1)")
        c.execute("INSERT INTO candidates (name, category_id) VALUES ('Shivaji',2)")
        c.execute("INSERT INTO candidates (name, category_id) VALUES ('MGR',2)")
        c.execute("INSERT INTO candidates (name, category_id) VALUES ('Vijay',3)")
    conn.commit()
    conn.close()

init_db()

def ai_response(query, lang="English"):
    # Fallback mechanism if API key is invalid or not set
    if not client:
        return _fallback_response(query, lang)

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
        return _fallback_response(query, lang)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return _fallback_response(query, lang)

def _fallback_response(query, lang="English"):
    """Provides mock responses when AI is down, with basic language support."""
    query = query.lower()
    
    # Dictionaries for basic translations
    responses = {
        "English": {
            "vote": "🗳️ **How to Vote:**<br>1. Register for Voter ID.<br>2. Check name in electoral roll.<br>3. Find booth.<br>4. Cast vote!",
            "process": "🏛️ **Election Process:**<br>Registration, campaigning, voting day, and counting of votes.",
            "default": "🤖 **Offline Mode:**<br>I'm unable to connect to the AI brain. Please use the Check Eligibility button on the left!"
        },
        "Hindi": {
            "vote": "🗳️ **वोट कैसे करें:**<br>1. वोटर आईडी के लिए रजिस्टर करें।<br>2. मतदाता सूची में नाम जांचें।<br>3. बूथ खोजें।<br>4. अपना वोट डालें!",
            "process": "🏛️ **चुनाव प्रक्रिया:**<br>पंजीकरण, प्रचार, मतदान दिवस, और वोटों की गिनती।",
            "default": "🤖 **ऑफ़लाइन मोड:**<br>मैं एआई से कनेक्ट नहीं हो पा रहा हूँ। कृपया बाईं ओर 'पात्रता जांचें' बटन का उपयोग करें!"
        },
        "Marathi": {
            "vote": "🗳️ **मतदान कसे करावे:**<br>1. मतदार ओळखपत्रासाठी नोंदणी करा.<br>2. मतदार यादीत नाव तपासा.<br>3. बूथ शोधा.<br>4. मतदान करा!",
            "process": "🏛️ **निवडणूक प्रक्रिया:**<br>नोंदणी, प्रचार, मतदानाचा दिवस आणि मतमोजणी.",
            "default": "🤖 **ऑफलाइन मोड:**<br>मी एआयशी कनेक्ट होऊ शकत नाही. कृपया डावीकडील 'पात्रता तपासा' बटण वापरा!"
        },
        "Bengali": {
            "vote": "🗳️ **কীভাবে ভোট দেবেন:**<br>1. ভোটার আইডির জন্য নিবন্ধন করুন।<br>2. ভোটার তালিকায় নাম চেক করুন।<br>3. বুথ খুঁজুন।<br>4. ভোট দিন!",
            "process": "🏛️ **নির্বাচন প্রক্রিয়া:**<br>নিবন্ধন, প্রচার, ভোটের দিন, এবং ভোট গণনা।",
            "default": "🤖 **অফলাইন মোড:**<br>আমি এআইয়ের সাথে সংযুক্ত হতে পারছি না। অনুগ্রহ করে বাম দিকের বোতাম ব্যবহার করুন!"
        }
    }
    
    # Ensure selected language exists in dictionary, fallback to English
    lang_dict = responses.get(lang, responses["English"])
    
    if "vote" in query or "how" in query or "कसे" in query or "कैसे" in query or "কীভাবে" in query:
        return lang_dict["vote"]
    elif "process" in query or "election" in query or "निवडणूक" in query or "चुनाव" in query:
        return lang_dict["process"]
    else:
        return lang_dict["default"]

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
    return render_template("dashboard.html")

@app.route("/categories")
def categories():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    data = []
    for cat in categories:
        c.execute("SELECT * FROM candidates WHERE category_id=?", (cat[0],))
        candidates = c.fetchall()
        data.append((cat, candidates))
    conn.close()
    return render_template("categories.html", data=data)

@app.route("/api/categories", methods=["POST"])
def add_category():
    name = request.json.get("name")
    if not name: return jsonify({"success": False})
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/categories/<int:id>", methods=["DELETE"])
def delete_category(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE id=?", (id,))
    c.execute("DELETE FROM candidates WHERE category_id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/voting-list")
def voting_list():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    data = []
    for cat in categories:
        c.execute("SELECT * FROM candidates WHERE category_id=?", (cat[0],))
        candidates = c.fetchall()
        data.append((cat, candidates))
    conn.close()
    return render_template("voting_list.html", data=data)

@app.route("/ai-assistant")
def ai_assistant():
    return render_template("ai_assistant.html")

@app.route("/education")
def education():
    return render_template("education.html")

@app.route("/users")
def users():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM voters")
    voters = c.fetchall()
    conn.close()
    return render_template("users.html", voters=voters)

@app.route("/api/register_voter", methods=["POST"])
def register_voter():
    data = request.json
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO voters (name, age, location) VALUES (?, ?, ?)", 
              (data.get("name"), data.get("age"), data.get("location")))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

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

@app.route("/voting")
def voting():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    data = []
    for cat in categories:
        c.execute("SELECT * FROM candidates WHERE category_id=?", (cat[0],))
        candidates = c.fetchall()
        data.append((cat, candidates))
    conn.close()
    return render_template("voting.html", data=data)

@app.route("/vote")
def vote():
    cid = request.args.get("id")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE candidates SET votes = votes + 1 WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/stats")
def stats():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT SUM(votes) FROM candidates")
    total_votes = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM voters")
    total_voters = c.fetchone()[0] or 0
    conn.close()
    return jsonify({
        "total_votes": total_votes,
        "total_voters": total_voters
    })

@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    data = []
    for cat in categories:
        c.execute("SELECT * FROM candidates WHERE category_id=?", (cat[0],))
        candidates = c.fetchall()
        data.append((cat, candidates))
    conn.close()
    return render_template("admin.html", data=data)

@app.route("/api/reset_votes", methods=["POST"])
def reset_votes():
    if request.json.get("password") != "admin123":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE candidates SET votes = 0")
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, threaded=True)
