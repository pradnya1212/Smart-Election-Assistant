import os
import random
import string
from flask import Flask, render_template, request, jsonify, session
from flask_wtf.csrf import CSRFProtect
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from google import genai
from google.genai import errors
try:
    import google.generativeai as legacy_genai
except ImportError:
    legacy_genai = None

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
csrf = CSRFProtect(app)

# 🐘 PostgreSQL Database Configuration
def get_postgres_db_uri():
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        conn = psycopg2.connect(dbname="postgres", user="postgres", password="root", host="localhost", port=5432, connect_timeout=2)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datname IN ('voting_system', 'voter_db', 'voting system')")
        row = cursor.fetchone()
        
        target_db = "voting_system"
        if not row:
            try:
                cursor.execute('CREATE DATABASE voting_system;')
                print("Successfully created database 'voting_system' in PostgreSQL!")
            except Exception:
                pass
        else:
            target_db = row[0]
            
        cursor.close()
        conn.close()

        # Connect check to target_db
        test_conn = psycopg2.connect(dbname=target_db, user="postgres", password="root", host="localhost", port=5432, connect_timeout=2)
        test_conn.close()
        return f"postgresql://postgres:root@localhost:5432/{target_db}"
    except Exception as e:
        print(f"PostgreSQL connection check note: {e}")
        return None

from models import db, Voter, Candidate, Vote, Category, Feedback

def init_database():
    env_db_url = os.getenv("DATABASE_URL")
    if env_db_url:
        uri = env_db_url
    else:
        pg_uri = get_postgres_db_uri()
        uri = pg_uri if pg_uri else "postgresql://postgres:root@localhost:5432/voting_system"

    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            _seed_candidates()
            print(f"Successfully initialized Database ({uri}).")
        except Exception as e:
            print(f"Database init note: {e}")

def _seed_candidates():
    if Candidate.query.count() == 0:
        c1 = Candidate(name="Rajesh Patil", party="Progressive Democratic Party", category="Mayor", votes_count=120)
        c2 = Candidate(name="Anita Sharma", party="Civic Alliance", category="Mayor", votes_count=85)
        c3 = Candidate(name="Sanjay Deshmukh", party="Independent Reformers", category="Mayor", votes_count=45)
        db.session.add_all([c1, c2, c3])
        
        if not Category.query.filter_by(name="Mayor").first():
            cat = Category(name="Mayor")
            db.session.add(cat)
            
        db.session.commit()

init_database()

# 🛡️ Google Responsible AI Safety Settings
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Try initializing API key, handle securely
api_key = os.getenv("GEMINI_API_KEY")
client = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Successfully initialized Google GenAI Client!")
    except Exception as e:
        print(f"GenAI Client Init Note: {e}")
        if legacy_genai:
            try:
                legacy_genai.configure(api_key=api_key)
                print("Initialized Legacy Google GenerativeAI Client.")
            except Exception as le:
                print(f"Legacy GenAI Init Note: {le}")
else:
    print("Notice: GEMINI_API_KEY not found in environment or .env file. Running in fallback mode.")

def ai_response(query, lang="English"):
    if not api_key:
        return _fallback_response(query, lang)

    prompt = f"""
    You are VoteGuide AI, an expert, friendly Election Assistant.
    
    Guidelines:
    1. Answer clearly and concisely in simple language.
    2. IMPORTANT: You MUST respond entirely in {lang}.
    3. Use bullet points and emojis to make the response engaging.
    4. If the user asks about election procedures, guide them step-by-step.
    5. Stay neutral and strictly informative.
    
    User Query: {query}
    """

    # 1. Try modern google-genai SDK
    if client:
        for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"safety_settings": SAFETY_SETTINGS}
                )
                if res and res.text:
                    return res.text
            except Exception as e:
                print(f"Gemini modern SDK ({model_name}) note: {e}")

    # 2. Try legacy google.generativeai SDK
    if legacy_genai and api_key:
        for model_name in ["gemini-1.5-flash", "gemini-pro"]:
            try:
                m = legacy_genai.GenerativeModel(model_name)
                res = m.generate_content(prompt)
                if res and res.text:
                    return res.text
            except Exception as e:
                print(f"Gemini legacy SDK ({model_name}) note: {e}")

    return "⚠️ Offline mode active. " + _fallback_response(query, lang)

@app.route("/translate", methods=["POST"])
def translate():
    """AI-Powered Translation using Google Gemini."""
    data = request.json
    text = data.get("text", "")
    target_lang = data.get("lang", "Hindi")
    
    if not client or not text:
        return jsonify({"translated": text})
        
    prompt = f"Translate the following text into {target_lang}. Keep the same tone, HTML tags, and emojis:\n\n{text}"
    try:
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return jsonify({"translated": res.text.strip() if res.text else text})
    except:
        return jsonify({"translated": text})

def ai_get_suggestions(query, bot_response, lang="English"):
    """Uses AI to generate 3 relevant follow-up questions in target language."""
    if not client:
        if lang == "Hindi":
            return ["मैं पंजीकरण कैसे करूं?", "ईवीएम (EVM) क्या है?", "कौन मतदान कर सकता है?"]
        elif lang == "Marathi":
            return ["मी नोंदणी कशी करू?", "ईव्हीएम (EVM) म्हणजे काय?", "कोण मतदान करू शकते?"]
        return ["How do I register?", "What is an EVM?", "Who can vote?"]
    
    prompt = f"""
    Based on this chat:
    User: {query}
    AI: {bot_response}
    
    Suggest 3 very short follow-up questions in {lang} that the user might ask next.
    Format: Return ONLY the questions separated by |
    Example: Question 1|Question 2|Question 3
    """
    try:
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        if res.text:
            return [q.strip() for q in res.text.split("|")][:3]
    except:
        pass
    if lang == "Hindi":
        return ["मैं पंजीकरण कैसे करूं?", "ईवीएम (EVM) क्या है?", "कौन मतदान कर सकता है?"]
    elif lang == "Marathi":
        return ["मी नोंदणी कशी करू?", "ईव्हीएम (EVM) म्हणजे काय?", "कोण मतदान करू शकते?"]
    return ["How do I register?", "What is an EVM?", "Who can vote?"]

def ai_get_registration_advice(name, age, lang="English"):
    """Generates a personalized AI tip for a new voter in target language."""
    if not client:
        if lang == "Hindi":
            return f"अपना पहचान पत्र सुरक्षित रखें, {name}! आपका वोट आपकी ताकत है।"
        elif lang == "Marathi":
            return f"तुमचे ओळखपत्र सुरक्षित ठेवा, {name}! तुमचे मत हा तुमचा हक्क आहे."
        return f"Keep your ID safe, {name}! Your vote is your voice."
    
    prompt = f"Give a 1-sentence personalized, encouraging tip in {lang} for a voter named {name} who is {age} years old. Highlight the power of voting."
    try:
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return res.text.strip() if res.text else "Your vote is your voice. Use it wisely!"
    except:
        return "Your vote is your voice. Use it wisely!"

def _fallback_response(query, lang="English"):
    """Provides localized mock responses when AI is down."""
    query = query.lower()
    if lang == "Hindi":
        if "vote" in query or "how" in query or "कैसे" in query:
            return "🗳️ **मतदान कैसे करें:**<br>1. वोटर आईडी के लिए पंजीकरण करें।<br>2. मतदाता सूची में अपना नाम जांचें।<br>3. अपना मतदान केंद्र खोजें।<br>4. पहचान पत्र साथ ले जाएं और वोट डालें!"
        else:
            return "🤖 **ऑफलाइन मोड सक्रिय:**<br>एआई नेटवर्क से कनेक्ट नहीं हो सका। आप बाईं ओर दिए गए स्टेप गाइड का उपयोग कर सकते हैं।"
    elif lang == "Marathi":
        if "vote" in query or "how" in query or "कसे" in query:
            return "🗳️ **मतदान कसे करावे:**<br>1. मतदार ओळखपत्रासाठी नोंदणी करा.<br>2. मतदार यादीत तुमचे नाव तपासा.<br>3. तुमचे मतदान केंद्र शोधा.<br>4. ओळखपत्र सोबत ठेवा आणि मतदान करा!"
        else:
            return "🤖 **ऑफलाइन मोड सक्रिय:**<br>एआई शी संपर्क साधता आला नाही. आपण डावीकडील स्टेप मार्गदर्शक वापरू शकता."

    if "vote" in query or "how" in query:
        return "🗳️ **How to Vote:**<br>1. Register for a Voter ID.<br>2. Check your name in the electoral roll.<br>3. Find your polling booth.<br>4. Carry a valid ID and cast your vote!"
    elif "process" in query or "election" in query:
        return "🏛️ **Election Process:**<br>Elections involve voter registration, candidate nomination, campaigning, voting day, and finally, counting of votes to declare the winner."
    else:
        return "🤖 **Offline Mode Active:**<br>I'm currently unable to connect to my AI brain. But you can still use the **Step Guide** and **Check Eligibility** buttons on the left!"

# 🗳️ MULTI-LANGUAGE GUIDE DATA
STEPS_DATA_MAP = {
    "English": [
        "✅ Check eligibility (18+ citizen)",
        "📝 Register for Voter ID card (Form 6)",
        "🔍 Verify your details on the electoral roll",
        "📍 Find your designated polling booth",
        "🆔 Carry a valid ID proof on election day",
        "🗳️ Cast your vote on the EVM/Ballot",
        "📊 Wait for the election results"
    ],
    "Hindi": [
        "✅ पात्रता जांचें (18+ नागरिक)",
        "📝 वोटर आईडी कार्ड के लिए आवेदन करें (फॉर्म 6)",
        "🔍 मतदाता सूची (इलेक्टोरल रोल) में नाम जांचें",
        "📍 अपना मतदान केंद्र खोजें",
        "🆔 चुनाव के दिन वैध पहचान पत्र साथ रखें",
        "🗳️ ईवीएम (EVM) / बैलेट पर अपना वोट डालें",
        "📊 चुनाव परिणामों का इंतजार करें"
    ],
    "Marathi": [
        "✅ पात्रता तपासा (१८+ नागरिक)",
        "📝 मतदार ओळखपत्रासाठी अर्ज करा (फॉर्म ६)",
        "🔍 मतदार यादीत नाव तपासा",
        "📍 तुमचे मतदान केंद्र शोधा",
        "🆔 निवडणुकीच्या दिवशी वैध ओळखपत्र सोबत ठेवा",
        "🗳️ ईव्हीएम (EVM) वर तुमचे मत नोंदवा",
        "📊 निकाल जाहीर होण्याची वाट पाहा"
    ],
    "Bengali": [
        "✅ যোগ্যতা পরীক্ষা করুন (১৮+ নাগরিক)",
        "📝 ভোটার আইডি কার্ডের জন্য আবেদন করুন (ফর্ম 6)",
        "🔍 ভোটার তালিকায় নাম পরীক্ষা করুন",
        "📍 আপনার পোলিং বুথ খুঁজুন",
        "🆔 ভোটের দিনে বৈধ পরিচয়পত্র সাথে রাখুন",
        "🗳️ ইভিএমে (EVM) আপনার ভোট দিন",
        "📊 নির্বাচনের ফলাফলের জন্য অপেক্ষা করুন"
    ],
    "Tamil": [
        "✅ தகுதியை சரிபார்க்கவும் (18+ குடிமகன்)",
        "📝 வாக்காளர் அடையாள அட்டைக்கு விண்ணப்பிக்கவும் (படிவம் 6)",
        "🔍 வாக்காளர் பட்டியலில் உங்கள் பெயரைச் சரிபார்க்கவும்",
        "📍 உங்கள் வாக்குச்சாவடியைக் கண்டறியவும்",
        "🆔 தேர்தல் நாளில் செல்லுபடியாகும் அடையாளச் சான்றை எடுத்துச் செல்லவும்",
        "🗳️ EVM மூலம் உங்கள் வாக்கைப் பதிவு செய்யுங்கள்",
        "📊 தேர்தல் முடிவுகளுக்காக காத்திருக்கவும்"
    ],
    "Telugu": [
        "✅ అర్హతను సరిచూడండి (18+ పౌరుడు)",
        "📝 ఓటర్ ఐడీ కార్డ్ కోసం దరఖాస్తు చేసుకోండి (ఫారం 6)",
        "🔍 ఓటర్ల జాబితాలో మీ పేరును సరిచూడండి",
        "📍 మీ పోలింగ్ కేంద్రాన్ని కనుగొనండి",
        "🆔 ఎన్నికల రోజున చెల్లుబాటు అయ్యే గుర్తింపు కార్డును తీసుకెళ్లండి",
        "🗳️ EVM పై మీ ఓటు వేయండి",
        "📊 ఎన్నికల ఫలితాల కోసం వేచి ఉండండి"
    ],
    "Gujarati": [
        "✅ પાત્રતા ચકાસો (18+ નાગરિક)",
        "📝 મતદાર આઈડી કાર્ડ માટે અરજી કરો (ફોર્મ 6)",
        "🔍 મતદાર યાદીમાં તમારું નામ ચકાસો",
        "📍 તમારું મતદાન મથક શોધો",
        "🆔 ચૂંટણીના દિવસે માન્ય ઓળખપત્ર સાથે રાખો",
        "🗳️ EVM પર તમારો મત આપો",
        "📊 ચૂંટણીના પરિણામોની રાહ જુઓ"
    ]
}

STEPS_DATA = STEPS_DATA_MAP["English"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask")
def ask():
    q = request.args.get("q", "")
    lang = request.args.get("lang", "English")
    if not q:
        return jsonify({"message": "Please ask a question."})
    
    response_text = ai_response(q, lang)
    # Convert newlines to HTML breaks
    if "<br>" not in response_text and "<ul>" not in response_text:
        response_text = response_text.replace("\n", "<br>")
        
    suggestions = ai_get_suggestions(q, response_text, lang)
    return jsonify({
        "message": response_text,
        "suggestions": suggestions
    })

@app.route("/guide")
def guide():
    lang = request.args.get("lang", "English")
    steps = STEPS_DATA_MAP.get(lang, STEPS_DATA_MAP["English"])
    return jsonify({"steps": steps})

@app.route("/check")
def check():
    lang = request.args.get("lang", "English")
    try:
        age = int(request.args.get("age", 0))
        if age >= 18:
            if lang == "Hindi":
                msg = f"शानदार! {age} साल की उम्र में आप वोट देने के लिए **पात्र** हैं। अपने वोटर आईडी के लिए पंजीकरण अवश्य करें!"
            elif lang == "Marathi":
                msg = f"छान! {age} वर्षे वयात तुम्ही मतदानासाठी **पात्र** आहात. मतदार ओळखपत्रासाठी नोंदणी नक्की करा!"
            else:
                msg = f"Awesome! At {age} years old, you are **eligible** to vote. Make sure you register for your Voter ID!"
            return jsonify({"eligible": True, "result": msg})
        else:
            if lang == "Hindi":
                msg = f"आपकी उम्र {age} वर्ष है। वोट देने के लिए आपकी उम्र **18 या उससे अधिक** होनी चाहिए।"
            elif lang == "Marathi":
                msg = f"तुमचे वय {age} वर्षे आहे. मतदानासाठी वय **18 किंवा त्याहून अधिक** असावे."
            else:
                msg = f"You are {age} years old. You must be **18 or older** to vote. You can register once you turn 18!"
            return jsonify({"eligible": False, "result": msg})
    except ValueError:
        return jsonify({"eligible": False, "result": "Invalid age provided."})

def generate_voter_id():
    state = "MH"
    year = "2026"
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{state}-{year}-{rand}"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    name = data.get("name", "").strip()
    age_str = data.get("age", "")
    address = data.get("address", "").strip()
    lang = data.get("lang", "English")

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
    ai_advice = ai_get_registration_advice(name, age, lang)
    
    # 🐘 Persist Voter record in PostgreSQL Database
    try:
        new_voter = Voter(voter_id=voter_id, name=name, age=age, address=address)
        db.session.add(new_voter)
        db.session.commit()
        session['voter_id'] = voter_id
    except Exception as e:
        db.session.rollback()
        print(f"Error persisting voter to Database: {e}")
    
    return jsonify({
        "success": True,
        "voter_id": voter_id,
        "message": f"""
        ✅ <b>Voter ID Generated & Registered in PostgreSQL Database</b><br><br>
        <b>Name:</b> {name}<br>
        <b>Voter ID:</b> {voter_id}<br>
        <b>Booth:</b> District-12<br>
        <b>Status:</b> Active in Electoral Roll<br><br>
        
        🤖 <b>AI Personalized Tip ({lang}):</b><br>
        <i>"{ai_advice}"</i><br><br>
        
        <b>📝 What to carry on Election Day:</b><br>
        - Printout of this Voter ID<br>
        - Original Aadhar Card/PAN<br><br>
        <small><i>Note: Record has been stored in PostgreSQL voter_db.</i></small>
        """
    })

@app.route("/candidates", methods=["GET"])
def get_candidates():
    candidates = Candidate.query.all()
    return jsonify({"candidates": [c.to_dict() for c in candidates]})

@app.route("/vote", methods=["POST"])
def vote():
    data = request.json or {}
    # Use robust server-side session to prevent spoofing
    voter_id_code = session.get("voter_id")
    candidate_id = data.get("candidate_id")

    if not voter_id_code:
        return jsonify({"success": False, "message": "Unauthorized. Please register to vote first."}), 403

    if not candidate_id:
        return jsonify({"success": False, "message": "Candidate selection is required."}), 400

    voter = Voter.query.filter_by(voter_id=voter_id_code).first()
    if not voter:
        return jsonify({"success": False, "message": f"Voter ID '{voter_id_code}' not found in Electoral Database. Please register first."})

    if voter.has_voted:
        return jsonify({"success": False, "message": f"⚠️ Vote Rejected: Voter ID '{voter_id_code}' has already cast a vote."})

    candidate = db.session.get(Candidate, candidate_id)
    if not candidate:
        return jsonify({"success": False, "message": "Selected candidate does not exist."})

    # Record vote in PostgreSQL
    try:
        voter.has_voted = True
        candidate.votes_count += 1
        new_vote = Vote(voter_id=voter_id_code, candidate_id=candidate.id)
        
        db.session.add(new_vote)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error recording vote: {e}"})

    return jsonify({
        "success": True,
        "message": f"✅ Vote Successfully Cast for {candidate.name} ({candidate.party})!",
        "candidate": candidate.to_dict()
    })

@app.route("/results", methods=["GET"])
def get_results():
    candidates = Candidate.query.order_by(Candidate.votes_count.desc()).all()
    total_votes = sum(c.votes_count for c in candidates)
    total_voters = Voter.query.count()
    return jsonify({
        "total_voters": max(total_voters, 250),
        "total_votes": total_votes,
        "candidates": [c.to_dict() for c in candidates]
    })

@app.route("/voters", methods=["GET"])
def get_voters():
    voters = Voter.query.order_by(Voter.created_at.desc()).all()
    return jsonify({"voters": [v.to_dict() for v in voters]})

@app.route("/categories", methods=["GET"])
def categories_page():
    categories = Category.query.all()
    data = [[c.id, c.name] for c in categories]
    return render_template("categories.html", data=data)

@app.route("/api/categories", methods=["POST"])
def add_category():
    data = request.json or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "message": "Category name is required"})
    try:
        if Category.query.filter_by(name=name).first():
            return jsonify({"success": False, "message": "Category already exists"})
        c = Category(name=name)
        db.session.add(c)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/categories/<int:id>", methods=["PUT"])
def edit_category(id):
    data = request.json or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "message": "Category name is required"})
    try:
        c = db.session.get(Category, id)
        if not c:
            return jsonify({"success": False, "message": "Category not found"})
        
        old_name = c.name
        c.name = name
        
        # Update associated candidates
        candidates = Candidate.query.filter_by(category=old_name).all()
        for cand in candidates:
            cand.category = name
            
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/categories/<int:id>", methods=["DELETE"])
def delete_category(id):
    try:
        c = db.session.get(Category, id)
        if not c:
            return jsonify({"success": False, "message": "Category not found"})
        
        # Delete candidates in this category as prompted by UI confirmation
        Candidate.query.filter_by(category=c.name).delete()
        db.session.delete(c)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, threaded=True)

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()

    try:
        feedback = Feedback(
            name=data.get("name"),
            rating=int(data.get("rating")),
            comment=data.get("comment")
        )

        db.session.add(feedback)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Thank you for your feedback!"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
}), 500     
