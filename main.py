from werkzeug.security import generate_password_hash,check_password_hash
from flask import Flask,render_template,request,redirect,url_for,session,flash,jsonify,send_file,request
import json
import google.generativeai as genai
import markdown
import re
import os
from googletrans import Translator
from fpdf import FPDF
import sqlite3
from flask_login import LoginManager, login_user, logout_user, login_required,UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import secrets
from flask import session
from google.oauth2 import id_token
from google.auth.transport import Request
import razorpay
from pymongo import MongoClient
from oauthlib.oauth2 import WebApplicationClient
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import ssl
import certifi
import requests
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


app=Flask(__name__,static_folder='static')
app.secret_key = "your_secret_key"
# ✅ Replace with your actual Google Gemini API Key
genai.configure(api_key="AIzaSyAu6hKGJgJLEFofXZ3Zp5apT60OnjY6xLY")
model = genai.GenerativeModel("gemini-2.0-flash") 
translator = Translator()
oauth = OAuth(app)
RAZORPAY_KEY_ID = "rzp_test_YyibBcCQWMgCjc"
RAZORPAY_KEY_SECRET = "dGhNK3vOmstB3CTPEquWdkUZ"
bcrypt = Bcrypt()

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

DEBUG_MODE = True
# MongoDB Connection
MONGO_URI = "mongodb+srv://hope_ai_domain:mGtFg5hhIV58TMFC@cluster0.71xtt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    print("Connected successfully!")
except Exception as e:
    print("Connection failed:", e)
db = client.hope_ai # Database Name
#db = SQLAlchemy(app)
client = WebApplicationClient("212679902873-q5f6ubo4pkqrj01tb5ig61j9fh8ctep7.apps.googleusercontent.com")
load_dotenv()

import os

mongo_uri = os.getenv("MONGODB_URI")
secret_key = os.getenv("SECRET_KEY")
razorpay_key = os.getenv("RAZORPAY_KEY_ID")

# Define MongoDB Collections
#print("Existing Collections:", db.list_collection_names())  # ✅ This will print all collections


users_collection = db["users"]
chats_collection = db["chats"]
transactions_collection = db["transactions"]
feedback_collection = db["feedback"]
website_generator_collection = db["website_generator_chats"]
code_optimizer_collection = db["code_optimizer_chats"]  #
translation_collection = db["translation_chats"]
email_generator_collection = db["email_generator_chats"]
proofreading_collection = db["proofreading_chats"]
story_writing_collection = db["story_writing_chats"]
mobile_marketing_collection = db["mobile_marketing_chats"]
seo_collection = db["seo_chats"]
youtube_script_collection = db["youtube_script_chats"]
press_release_collection = db["press_release_chats"]

login_manager = LoginManager()
login_manager.init_app(app)  # Attach login_manager to Flask app
login_manager.login_view = "login"  # Define the login ro # Generate a secure nonce
# User loader function
class User(UserMixin):
    def __init__(self, user_id, email, name):
        self.id = str(user_id)
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(user["_id"], user["email"], user["name"])
    return None

#class User(db.Model, UserMixin):
    # id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.String(100), nullable=False)
    #email = db.Column(db.String(100), unique=True, nullable=False)
    #password = db.Column(db.String(300), nullable=False)
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)

app.config['GOOGLE_CLIENT_ID'] =  os.getenv("GOOGLE_CLIENT_ID")
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET")
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],  # ✅ FIXED: Using correct key
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],  # ✅ FIXED: Using correct key
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url=app.config['GOOGLE_DISCOVERY_URL']
    
    )

generation_count=0

@app.route('/')
def index():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return "You are already registered! Please log in."

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }

        users_collection.insert_one(new_user)
        print(ssl.OPENSSL_VERSION)

        return redirect(url_for("login"))

    return render_template("signup.html")

    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_collection.find_one({"email": email})
        if user and bcrypt.check_password_hash(user["password"], password):
            user_obj = User(user["_id"], user["email"], user["name"])
            login_user(user_obj)  # Ensure user is logged in properly

            session["user_id"] = str(user["_id"])
            session["email"] = user["email"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid email or password!"

    return render_template("login.html")


@app.route("/login/google")
def google_login():
    """Redirects users to Google Sign-In Page."""
    google_provider_cfg = requests.get("https://accounts.google.com/.well-known/openid-configuration").json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="http://localhost:5000/login/google/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/google/callback")
def google_callback():
    """Handles Google OAuth response and stores user in MongoDB."""
    code = request.args.get("code")

    google_provider_cfg = requests.get("https://accounts.google.com/.well-known/openid-configuration").json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url="http://localhost:5000/login/google/callback",
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET']),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    user_info = userinfo_response.json()

    if "email" not in user_info:
        return "User email not available", 400

    # Check if user already exists in MongoDB
    existing_user = users_collection.find_one({"email": user_info["email"]})


    if existing_user:
        # User exists, log them in
        session.clear()
        session["user_id"] = str(existing_user["_id"])
        session["email"] = existing_user["email"]
        session["name"] = existing_user["name"]
        login_user(User(existing_user["_id"], existing_user["email"], existing_user["name"]))  # ✅ Ensure user is logged in
        return redirect(url_for("dashboard"))

    # Store new user in MongoDB
    user_data = {
        "google_id": user_info["sub"],
        "name": user_info["name"],
        "email": user_info["email"],
        "profile_pic": user_info["picture"],
        "created_at": datetime.utcnow()
    }

    new_user_id = users_collection.insert_one(user_data).inserted_id

    # Start a session
    session.clear()
    session["user_id"] = str(user_data["_id"])
    session["email"] = user_data["email"]
    session["name"] = user_data["name"]
    login_user(User(new_user_id, user_info["email"], user_info["name"]))  # ✅ Ensure new user is logged in


    return redirect(url_for("dashboard"))



@app.route("/dashboard")
@login_required
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = users_collection.find_one({"_id": ObjectId(session["user_id"])})

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)
    #return render_template("dashboard.html")


@app.route('/services')
def services():
    return render_template('sevice.html')

def track_generations():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the user has a stored generation count
    current_count = user.get("generation_count", 0)

    if current_count >= 5:  # Limit reached
        return redirect(url_for("pricing"))  # Redirect to pricing page

    # Increment the count
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"generation_count": current_count + 1}})
    return None  # Allow AI generation

@app.route("/generate-content", methods=["POST"])
def generate_content():
    """AI-Powered Blog, Resume, and Ad Copy Generator"""

    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Track user generations
    redirect_response = track_generations()
    if redirect_response:
        return redirect_response  # Stop generation if limit is reached


    # Get JSON data from frontend
    data = request.json
    content_type = data.get("content_type", "").strip().lower()
    topic = data.get("topic", "").strip()
    length = data.get("length", "300")  # Default to 300 words

    # Validate Inputs
    if not content_type or not topic:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        length = int(length)  # Convert to integer
    except ValueError:
        return jsonify({"error": "Invalid content length"}), 400
    
    # Define AI Prompt Based on Content Type
    prompt_template = {
"blog": f"""
Generate like experience blog writer and a **high-quality, professional, and SEO-optimized** blog on "{topic}".
Ensure the blog has **real-world examples, case studies, and statistics** for credibility.

**Blog Structure:**  
1️⃣ **Meta Title & Meta Description:**  
   - Create a compelling blog title and a **160-character meta description** with **focus keywords**.  

2️⃣ **Introduction:**  
   - Hook the reader with an **attention-grabbing opening**.  
   - Explain why this topic matters in **2-3 engaging sentences**.  

3️⃣ **Main Content:**  
   - **Use H2 & H3 headings, bullet points, and short paragraphs** for readability.  
   - Add **real-world statistics, case studies, and expert opinions** (e.g., "According to Forbes, AI adoption grew by 57% in 2023").  
   - Compare **industry leaders, historical trends, or best practices** if relevant.  

4️⃣ **Challenges & Solutions:**  
   - Identify **common challenges & proven solutions** in this field.  
   - Mention **best practices, expert advice, or research-backed strategies**.  

5️⃣ **Government Policies & Regulations (if applicable):**  
   - Discuss **tax incentives, legal regulations, and industry policies** related to {topic}.  
   - Mention relevant regulatory bodies (e.g., GDPR for data privacy, FDA for health, SEC for finance).  

6️⃣ **SEO Optimization:**  
   - Naturally insert **primary & LSI keywords** to improve search rankings.  
   - Suggest **internal/external links** to credible sources (e.g., "Harvard Business Review," "World Economic Forum").  

7️⃣ **Conclusion & Call-to-Action (CTA):**  
   - Summarize key takeaways in **2-3 bullet points**.  
   - Include a **CTA** (e.g., "Share your thoughts in the comments!" or "Subscribe for more insights!").  

🔹 **Formatting Guidelines:**  
- Use **Markdown formatting** (e.g., `#` for H1, `##` for H2, `###` for H3).  
- Ensure **zero factual errors** (mention only **verified information**).  
- Keep paragraphs **concise & easy to read**.  

**Example Enhancements for Different Topics:**  
- **Technology:** "OpenAI reports that ChatGPT reached 100M users in 2 months."  
- **Finance:** "S&P 500 had an annual return of 10.5% over the last 30 years."  
- **Health:** "Harvard Medical School states that regular exercise reduces heart disease risk by 30%."  
- **Business:** "90% of startups fail within the first five years—here's how to avoid common mistakes."  
""",

        "resume": f"""
        Generate a professional resume for an individual with experience in "{topic}".
        Ensure the resume is formatted properly with clear sections.

        **Structure:**
        - **Name & Contact Info**
        - **Professional Summary**: A short introduction
        - **Skills**: Bullet-point list of key skills
        - **Work Experience**: Job roles, companies, and key achievements
        - **Education**: Degrees and certifications
        - **Projects**: Notable work and achievements

        Content length: {length} words.
        Format the response using Markdown for clarity.
        """,

        "ad_copy": f"""
        Generate like professional human freelancer a compelling ad copy for promoting "{topic}".
        Ensure the ad is engaging, persuasive, and well-structured.

        **Structure:**
        - **Headline**: Eye-catching and engaging
        - **Body**: Clear message that highlights the benefits
        - **Call to Action (CTA)**: Encourages the audience to take action

        Content length: {length} words.
        Format the response using Markdown for clarity.
        """
    }

    # Call Gemini AI to Generate Content
    prompt = prompt_template.get(content_type, "Write a general article.")
    response = model.generate_content(prompt)

    # Ensure AI Response is Valid
    if response and hasattr(response, "text"):
        generated_text = response.text.strip()
        session["ai_content"] = generated_text
        session.modified = True
    else:
        generated_text = "⚠ AI could not generate content. Try again."

    if not generated_text.strip():
        session.pop("ai_content", None)

    if "user_id" in session:
        chat_data = {
    "user_id": session["user_id"],
    "generator_type": content_type,
    "user_input": topic,
    "ai_response": generated_text,
            "timestamp": datetime.utcnow()
        }
        if content_type == "blog":
            db["blog_chats"].insert_one(chat_data)  # ✅ Store blog chats in "blog_chats"
        elif content_type == "resume":
            db["resume_chats"].insert_one(chat_data)  # ✅ Store resume chats correctly
        elif content_type == "ad_copy":
            db["ad_copy_chats"].insert_one(chat_data)
        else:
            chats_collection.insert_one(chat_data)  # ✅ Store other chat data in "chats_collection"
        #limit_response = track_generations()
    #if limit_response:
        #return limit_response 
    return jsonify({"generated_content": generated_text})

    
@app.route("/check-session")
def check_session():
    return jsonify({"ai_content": session.get("ai_content", "Not Stored")})

@app.route("/create_order", methods=["POST"])
def create_order():
    try:
        data = request.json
        amount = int(data["amount"]) * 100  # Convert to paise (Razorpay uses paise)
        currency = "INR"
        receipt = f"order_rcpt_{secrets.token_hex(8)}"

        # Create an order on Razorpay
        order = razorpay_client.order.create({
            "amount": amount,
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1
        })

        return jsonify({"order_id": order["id"]})

    except Exception as e:
        print("Razorpay Error:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500

@app.route("/verify_payment", methods=["POST"])
def verify_payment():
    try:
        data = request.json
        payment_id = data["payment_id"]
        amount = data["amount"]

        # Verify the payment using Razorpay API
        payment_details = razorpay_client.payment.fetch(payment_id)

        if payment_details["status"] == "captured":
            # Store the transaction in the database
            transaction_data = {
                "user_id": session["user_id"],
                "amount": amount,
                "payment_id": payment_id,
                "status": "Success",
                "timestamp": datetime.utcnow()
            }
            transactions_collection.insert_one(transaction_data)

            return jsonify({"message": "Payment successful and recorded!"})
        else:
            return jsonify({"error": "Payment failed!"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate-website', methods=['POST'])
def generate_website():
    try:
        data = request.json
        business_type = data.get("businessType", "").strip()
        features = data.get("features", "").strip()

        if not business_type or not features:
            return jsonify({"error": "Missing required fields"}), 400

        # AI prompt for website generation
        prompt = f"""
        Create a professional, responsive Bootstrap website for a {business_type} business.
        Features: {features}. Use Bootstrap for styling and ensure it is mobile-friendly.
        Provide a full HTML document including <html>, <head>, and <body> tags.
        """

        model = genai.GenerativeModel("gemini-2.0-flash")  # Ensure the correct model is used
        response = model.generate_content(prompt)

        # Debugging: Print AI response
        #print("AI Response:", response.text)  # ✅ THIS WILL SHOW AI OUTPUT

        if not response.text or "<html" not in response.text.lower():
            return jsonify({"error": "AI did not generate a valid HTML output."}), 500
        
        website_chat_data = {
    "user_id": session["user_id"],
    "generator_type": "Website Generator",
    "user_input": f"Business Type: {business_type}, Features: {features}",
    "ai_response": response.text[:1000],  # Store first 1000 characters
    "timestamp": datetime.utcnow()
        }
        website_generator_collection.insert_one(website_chat_data)
        generation_count=+1
        print(generation_count)
        return jsonify({"website_code": response.text})
        
    except Exception as e:
        print("Flask API Error:", str(e))  # ✅ This prints errors if API fails
        return jsonify({"error": str(e)}), 500



# 🔹 AI Code Optimizer
@app.route("/optimize-code", methods=["POST"])
def optimize_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        if not code:
            return jsonify({"error": "No code provided!"}), 400

        # Debugging logs
        print(f"Received code for optimization: {code}")

        # AI model request
        prompt = f"""
        Your task is to analyze and optimize the given code by fixing syntax errors, 
        formatting it correctly, and ensuring all elements are properly closed.and give the explanation
        what error has done in the code 

        ### Input Code:
        {code}

        ### Optimized Code:
        """

        response = model.generate_content(prompt)  # ✅ Correct function

        if not response or not response.text:
            raise ValueError("No response received from AI model")

        optimized_code = response.text.strip()
        code_optimizer_chat_data = {
    "user_id": session["user_id"],
    "generator_type": "Code Optimizer",
    "user_input": code,
    "ai_response": optimized_code[:1000],  # Storing first 1000 characters
    "timestamp": datetime.utcnow()
        }
        code_optimizer_collection.insert_one(code_optimizer_chat_data)
    
        generation_count=+1
        print(generation_count)
        return jsonify({"optimized_code": optimized_code})

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Logs error to terminal
        return jsonify({"error": str(e)}), 500

    


#
# Define correct ISO language codes
LANGUAGE_CODES = {
    "Hindi": "hi",
    "German": "de",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "kannada":"kan",
    "Telugu":"tel",
    "Marathi":"mar",
    "Gujarati":"gur",
    "Urdu":"urdu",
    "Malayalam":"malya",
    "Bengali":"ben",
    "Tamil":"ta"       
 }

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json(force=True)
        text = data.get('text')
        target_language = data.get('dest_lang')

        if not text or not target_language:
            return jsonify({'error': 'Missing text or target language'}), 400

        #  Ensure correct language code is used
        target_lang_code = LANGUAGE_CODES.get(target_language, target_language)

        model = genai.GenerativeModel('gemini-2.0-flash')

        #  Force strict translation with correct output language
        prompt = (f"think you as a professional transltor and Translate the following text into {target_language} ({target_lang_code}). "
                  "Return only the translated text, without any extra words:\n\n"
                  f"Text: {text}\n"
                  f"Translation ({target_language}):")

        response = model.generate_content(prompt)
        translated_text = response.text.strip() if response else "Translation failed"
        if "user_id" in session:
            translation_chat = {
        "user_id": session["user_id"],
        "generator_type": "Translation",
        "user_input": f"Original Text: {text}, Target Language: {target_language}",
        "ai_response": translated_text,
        "timestamp": datetime.utcnow()
            }
            translation_collection.insert_one(translation_chat)

        #  Extra check: If output is still in English, force retranslation
        if translated_text.lower() == text.lower():
            translated_text = f"Error: Translation to {target_language} failed."
        
        return jsonify({'translated_text': translated_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
generation_count=+1
print(generation_count)
@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        # 🔥 DEBUG: Print raw request data to check for encoding issues
        print("Raw Request Data:", request.data.decode("utf-8"))

        # ✅ Try parsing JSON manually
        data = json.loads(request.data.decode("utf-8"))

        # ✅ Ensure JSON format is correct
        if not isinstance(data, dict):
            print("❌ Error: Data is not a valid JSON object")
            return jsonify({'error': 'Invalid JSON format'}), 400

        email_type = data.get('email_type')
        details = data.get('details')

        if not email_type or not details:
            print("❌ Error: Missing email type or details")  # ✅ Debugging log
            return jsonify({'error': 'Missing email type or details'}), 400

        # ✅ Fix Encoding Issues (handling curly quotes)
        details = details.encode("utf-8").decode("utf-8")

        # ✅ Modify AI Prompt to Ensure Subject is Included
        prompt = f"""
        Generate a professional {email_type} email with the following details:
        {details}

        **Email Structure:**
        - **Subject:** A clear, engaging subject line.
        - **Body:** The full email content.
        **Guidelines:**
        - Ensure the tone matches the email type (e.g., persuasive for marketing, professional for business).
        - Use **engaging and powerful language** to capture interest.
        - Keep it **concise and impactful** (avoid excessive wordiness).
        - Strengthen the **call-to-action (CTA)** (make it urgent and action-driven).
        - Highlight **real business impact** (time savings, revenue growth, efficiency gains).
        - Add **a sense of urgency** to increase conversions.

        Return your response in this format:
        **Subject:** [Generated Subject]
        **Body:** [Generated Email Body]
        """

        response = model.generate_content(prompt)

        if response and hasattr(response, 'text'):
            email_text = response.text.strip()

            # ✅ Extract Subject & Body
            subject_match = re.search(r"\*\*Subject:\*\* (.*?)\n", email_text)
            body_match = re.search(r"\*\*Body:\*\*(.*)", email_text, re.DOTALL)

            subject = subject_match.group(1).strip() if subject_match else "No Subject Generated"
            body = body_match.group(1).strip() if body_match else "Error: Email body not generated."
            formatted_body = body.replace("\n", "<br>")
            if "user_id" in session:
                email_chat = {
                    "user_id": session["user_id"],
                    "generator_type": "Email Generator",
                    "user_input": f"Email Type: {email_type}, Details: {details}",
                    "ai_response": f"Subject: {subject}\n\n{body}",
                    "timestamp": datetime.utcnow()
                }
                email_generator_collection.insert_one(email_chat)


            generation_count=+1
            print(generation_count)
            return jsonify({"subject": subject, "email": body})

        else:
            return jsonify({"error": "Error: AI could not generate an email."}), 500

    except Exception as e:
        print(f"❌ Flask Error: {str(e)}")  # ✅ Debugging log
        return jsonify({"error": str(e)}), 500
    
def proofread_text(input_text):
    """Function to send text to Gemini AI and get the proofread version."""
    model = genai.GenerativeModel("gemini-2.0-flash")

    try:
        prompt = f"""
        Improve the following text by focusing on:
        - Making it concise and removing unnecessary words
        - Strengthening business tone and clarity
        - Using active voice instead of passive voice
        - Ensuring correct punctuation and sentence structure
        - Formatting it for readability
        - Providing **three variations** of the text: **Formal, Casual, and Executive-Level**

        Text:
        {input_text}

        **Return the response in this format:**
        **Formal:** [Improved formal version]  
        **Casual:** [Improved casual version]  
        **Executive:** [Improved high-level business version]  
        """

        response = model.generate_content(prompt)


        # ✅ Ensure response contains valid output
        if response and response.candidates:
            if response.candidates[0].finish_reason == 3:  # Safety Violation
                return "⚠️ AI blocked this content due to safety concerns."

            return response.text.strip() if hasattr(response, 'text') else "⚠️ AI could not generate a valid response."

        return "⚠️ No response received from AI."

    except Exception as e:
        print(f"❌ Error: {e}")
        return "⚠️ An error occurred while processing the request."

@app.route("/proofread", methods=["POST"])
def proofread():
    """API endpoint to receive text, process it with AI, and return the edited version."""
    data = request.json
    input_text = data.get("text", "").strip()
    
    if not input_text:
        return jsonify({"error": "No text provided"}), 400
    
    edited_text = proofread_text(input_text)

    if "user_id" in session:
            proofreading_chat = {
                "user_id": session["user_id"],
                "generator_type": "Proofreading & Editing",
                "user_input": input_text,
                "ai_response": edited_text,
                "timestamp": datetime.utcnow()
            }
            proofreading_collection.insert_one(proofreading_chat)
            generation_count=+1
            print(generation_count)
    return jsonify({"original": input_text, "corrected_text": edited_text})

@app.route("/generate-story", methods=["POST"])
def generate_story():
    """AI Story Writing API"""
    data = request.json
    theme = data.get("theme", "").strip()
    genre = data.get("genre", "").strip()
    length = data.get("length", "").strip()

    if not theme or not genre or not length:
        return jsonify({"error": "Missing required inputs (theme, genre, length)."}), 400

    # Define AI prompt for story generation
    prompt = f"""
    You are a **highly skilled fiction writer** known for crafting **deep, immersive, and suspenseful stories**.
    Your task is to **generate a captivating short story** with a **strong beginning, middle, and end**, filled with mystery, tension, and an unexpected twist.

    ### **📌 Story Structure & Requirements:**  
    ✅ **Engaging Hook (First 2-3 sentences)** → Draw the reader in immediately with **atmosphere, suspense, or action**.  
    ✅ **Character Depth** → Give the protagonist and key characters **emotional depth, personal stakes, and realistic reactions**.  
    ✅ **Foreshadowing for the Twist** → Drop **subtle clues** that hint at the final revelation **without making it too obvious**.  
    ✅ **Strong Pacing & Suspense** → Use **pauses, sensory details, and short/long sentence variation** to build tension.  
    ✅ **Immersive Setting & Mood** → Create **a vivid gothic, eerie, or mysterious environment** with **rich descriptions**.  
    ✅ **Unpredictable & Satisfying Twist** → The ending should be **clever, unexpected, yet make complete sense** in hindsight.  
    ✅ **Smooth & Logical Conclusion** → Resolve the mystery while leaving **a lingering sense of wonder or dread**.  

    ### **🎭 Writing Style & Techniques:**  
    📌 **Use deep, sensory descriptions** (e.g., *The air smelled of mildew and forgotten time* instead of *It was an old house*).  
    📌 **Add brief emotional reflections** (e.g., *A childhood memory flickered—had she been here before?*).  
    📌 **Use immersive dialogue & inner thoughts** to make characters feel real.  
    📌 **Subtly foreshadow the twist early** (e.g., *Something about the paintings felt… familiar. Too familiar.*).  
    📌 **End with a powerful closing line** that **leaves a lasting impact**.  
    📌 **Deepen emotional responses** → When a shocking discovery happens, describe the character’s **physical reactions, inner turmoil, and conflicting emotions**.  
    📌 **Enhance pacing near the climax** → Let key moments **breathe** before the final revelation.  
    📌 **Include subtle hints about the mystery throughout the story** → These should be noticeable **only in hindsight** after the twist is revealed.  

    **Example Format:**  
    <center><h2>Story Title</h2></center>
    
    **Story:**  
    [An engaging, immersive, and unpredictable AI-generated story]  
    
    Now, generate a **{length}** word **{genre}** story based on the theme: **{theme}**.
    """

    # Send request to Gemini AI
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    # Check AI response
    if response and hasattr(response, "text"):
        story_chat = {
            "user_id": session["user_id"],
            "generator_type": "Story Writing",
            "user_input": f"Theme: {theme}, Genre: {genre}, Length: {length}",
            "ai_response": response.text[:1000],
            "timestamp": datetime.utcnow()
        }
        story_writing_collection.insert_one(story_chat)
        generation_count=+1
        print(generation_count)
        return jsonify({"story": response.text.strip()})

    return jsonify({"error": "AI could not generate a valid story."}), 500

@app.route("/generate-marketing", methods=["POST"])
def generate_marketing():
    """AI-Powered Mobile Marketing API"""
    data = request.get_json()
    campaign_type = data.get("campaign_type", "").strip().lower()
    product_details = data.get("product_details", "").strip()

    if not campaign_type or not product_details:
        return jsonify({"error": "Missing campaign type or product details."}), 400

    # Define a more structured AI prompt to ensure relevance
    campaign_prompts = {
        "sms": f"""
        Generate a **short and engaging SMS** for promoting **{product_details}**.  

        ✅ **Rules for SMS:**  
        - Maximum **160 characters**.  
        - Start with an **attention-grabbing phrase** (e.g., "🔥 Huge Sale!").  
        - **Highlight the key offer** or benefit.  
        - Include a **clear Call-To-Action (CTA)** (e.g., "Shop Now!", "Claim Your Offer!").  
        - **No unnecessary words or random names!**  
        """,

        "whatsapp": f"""
        Generate a **WhatsApp marketing message** for **{product_details}**.  

        ✅ **Rules for WhatsApp:**  
        - Start with a **friendly greeting** (e.g., "Hey [UserName] 🎉").  
        - Use a **conversational and engaging tone**.  
        - Include a **strong CTA** (e.g., "Click here to grab your deal!").  
        - **No random words or unrelated content!**  
        """,

        "push_notification": f"""
        Generate a **short, action-driven Push Notification** for **{product_details}**.  

        ✅ **Rules for Push Notifications:**  
        - Maximum **50-80 characters**.  
        - Use urgency (e.g., "🚨 Last Chance!").  
        - Keep it **short, powerful, and engaging**.  
        - **No unnecessary words or irrelevant names!**  
        """
    }

    prompt = campaign_prompts.get(campaign_type, "Generate a short marketing message.")

    # Send request to AI
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    

    if response and hasattr(response, "text"):
        formatted_message = response.text.strip()  # ✅ Get only the text
    else:
        formatted_message = "⚠ AI response could not be retrieved."  
    marketing_chat = {
                "user_id": session["user_id"],
                "generator_type": "Mobile Marketing",
                "user_input": f"Campaign Type: {campaign_type}, Product: {product_details}",
                "ai_response": formatted_message,
                "timestamp": datetime.utcnow()
            }
    mobile_marketing_collection.insert_one(marketing_chat)
    generation_count=+1
    print(generation_count)
    return jsonify({"marketing_message": formatted_message})

    return jsonify({"error": "AI could not generate marketing content."}), 500


def generate_meta_description(content):
   """Generate an optimized, engaging SEO meta description using Gemini AI."""
   prompt = f"""
    Write a **concise, engaging, SEO-friendly meta description (max 160 characters)** for the topic:  
    **'{content}'**  

    ✅ **Keep it under 160 characters** for better Google ranking.  
    ✅ **Include the primary keyword naturally.**  
    ✅ **Make it action-driven** with a Call-To-Action (CTA).  

    Format: **One single-line meta description**  
    """
   response = model.generate_content(prompt)  # ✅ Correct function
   return response.text.strip() if hasattr(response, "text") else "⚠ AI could not generate a meta description."


def suggest_keywords(content):
   """Generate SEO-friendly keywords using Gemini AI with high accuracy."""
   prompt = f"""
    You are an expert **SEO strategist**. Your task is to generate **5 high-ranking SEO keywords** for the topic:  
    **'{content}'**  

    ✅ **Prioritize keywords with high search volume** (based on Google SEO trends).  
    ✅ **Include LSI (Latent Semantic Indexing) keywords** for better ranking.  
    ✅ **Ensure keywords are short, clear, and optimized for search engines.**  
    ✅ **Format response as a comma-separated list** without numbering.  
    """
   response = model.generate_content(prompt)  # ✅ Correct function
   return response.text.strip().split(',') if hasattr(response, "text") else ["Keyword generation failed"]


def optimize_content(content):
    """Optimize content by inserting keywords naturally."""
    keywords = suggest_keywords(content)
    optimized_content = content
    prompt = f"""
    You are a professional **SEO content writer**. Improve the readability of the following content:  
    **'{content}'**  

    ✅ **Use engaging power words** like "game-changing," "breakthrough," "next-gen," "cutting-edge."  
    ✅ **Keep sentences short** (max 20 words per sentence) for mobile readability.  
    ✅ **Naturally integrate SEO keywords** without overstuffing.  
    ✅ **Use H1, H2, and bullet points for better readability.**  
    ✅ **Include a Call-To-Action (CTA) at the end** to boost engagement.  

    Format: **Well-structured content with headings, short paragraphs, and bullet points.**  
    """
    
    response = model.generate_content(prompt)
    
    return response.text.strip() if hasattr(response, "text") else optimized_content, keywords


@app.route('/seo-optimize', methods=['POST'])
def seo_optimize():
    """API endpoint to optimize content for SEO."""
    data = request.json
    content = data.get("content", "")

    if not content:
        return jsonify({"error": "No content provided"}), 400

    optimized_content, keywords = optimize_content(content)
    meta_description = generate_meta_description(content)

    # Ensure proper paragraph formatting
    formatted_content = optimized_content.replace("\n", "<br><br>")
    seo_chat = {
            "user_id": session["user_id"],
            "generator_type": "SEO Optimization",
            "user_input": content[:200],
            "ai_response": formatted_content[:1000],
            "timestamp": datetime.utcnow()
        }
    seo_collection.insert_one(seo_chat)
    generation_count=+1
    print(generation_count)
    return jsonify({
        "optimized_content": optimized_content,
        "keywords": keywords,
        "meta_description": meta_description
    })
@app.route("/generate-youtube-script", methods=["POST"])
def generate_youtube_script():
    try:
        data = request.get_json()
        topic = data.get("topic", "No Topic Provided")
        target_audience = data.get("target_audience", "No Audience Provided")
        video_length = data.get("video_length", "Unknown Length")

        prompt = f"Generate a YouTube script for the topic '{topic}', targeting '{target_audience}', with a duration of {video_length} minutes."

        response = model.generate_content(prompt)

        # ✅ Debugging Log to Check AI Response
        #print("🔍 AI Response:", response)

        # ✅ Ensure response contains text
        if response and hasattr(response, "text"):
            script_text = response.text.strip()
        else:
            script_text = "⚠ AI response could not be retrieved."

        youtube_chat = {
            "user_id": session.get("user_id", "Unknown"),
            "generator_type": "YouTube Script",
            "user_input": f"Topic: {topic}, Audience: {target_audience}, Length: {video_length} minutes",
            "ai_response": script_text[:1000],  # ✅ Store only text
            "timestamp": datetime.utcnow()
        }

        ## ✅ Debugging Log Before Database Insertion
        #print("📌 Inserting into MongoDB:", youtube_chat)

        youtube_script_collection.insert_one(youtube_chat)
        generation_count=+1
        print(generation_count)
        return jsonify({"script": script_text})

    except Exception as e:
        print("❌ ERROR in /generate-youtube-script:", str(e))  # ✅ Print full error in Flask console
        return jsonify({"error": str(e)}), 500


def generate_cover_letter(name, job_title, experience, skills):
    """Generates a personalized AI-powered cover letter."""
    prompt = f"""
    Write a compelling cover letter for {name} applying for {job_title}.
    - **Experience**: {experience}.
    - **Skills**: {skills}.
    Keep it **engaging, concise, and tailored** for the job role.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()
def generate_resume(name, job_title, experience, skills, education, start_date, end_date):
    """Generates a structured AI-powered resume."""
    prompt = f"""
    Generate a professional resume for {name}, applying for {job_title}.
    - **Experience**: {experience}. Highlight at least 2 impact-driven achievements.
    - **Skills**: {skills}.
    - **Education**: {education} ({start_date} - {end_date}).
    Format it properly without placeholders like [Your Address], [Your Phone Number], etc.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_cover_letter(name, job_title, experience, skills):
    """Generates a personalized AI-powered cover letter."""
    prompt = f"""
    Write a compelling cover letter for {name} applying for {job_title}.
    - **Experience**: {experience}.
    - **Skills**: {skills}.
    Keep it **engaging, concise, and tailored** for the job role.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

@app.route("/generate-resume", methods=["POST"])
def generate_resume_api():
    """API to generate AI-powered resume & cover letter."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request, JSON data missing"}), 400

    name = data.get("name", "").strip()
    job_title = data.get("job_title", "").strip()
    experience = data.get("experience", "Not provided").strip()
    skills = data.get("skills", "Not provided").strip()
    education = data.get("education", "Not provided").strip()
    start_date = data.get("start_date", "N/A").strip()
    end_date = data.get("end_date", "N/A").strip()

    if not name or not job_title:
        return jsonify({"error": "Name and job title are required"}), 400

    # ✅ Pass all arguments correctly
    resume_text = generate_resume(
        name=name,
        job_title=job_title,
        experience=experience,
        skills=skills,
        education=education,
        start_date=start_date,
        end_date=end_date
    )
    
    cover_letter_text = generate_cover_letter(name, job_title, experience, skills)
    generation_count=+1
    print(generation_count)
    return jsonify({"resume": resume_text, "cover_letter": cover_letter_text})

@app.route("/download-resume", methods=["POST"])
def download_resume():
    """API to generate & download resume as PDF."""
    data = request.json
    resume_text = data.get("resume", "Resume data not available")
    cover_letter_text = data.get("cover_letter", "Cover letter data not available")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Resume", ln=True, align="C")
    pdf.multi_cell(0, 10, resume_text)

    pdf.add_page()
    pdf.cell(200, 10, "Cover Letter", ln=True, align="C")
    pdf.multi_cell(0, 10, cover_letter_text)

    pdf_filename = "AI_Resume.pdf"
    pdf.output(pdf_filename)

    return send_file(pdf_filename, as_attachment=True)


@app.route("/generate-press-release", methods=["POST"])
def generate_press_release():
    """Generate an AI-powered Press Release"""
    data = request.json

    press_type = data.get("pressType", "").strip()
    headline = data.get("headline", "").strip()
    key_details = data.get("keyDetails", "").strip()
    contact_info = data.get("contactInfo", "").strip()

    if not press_type or not headline or not key_details or not contact_info:
        return jsonify({"error": "Missing required fields"}), 400

    # AI Prompt Template
    prompt = f"""
    Write a professional **{press_type.replace("_", " ")}** press release.
    
    **Headline:**  
    - {headline}

    **FOR IMMEDIATE RELEASE**  
    - {key_details}  

    **Official Statement:**  
    - Include an expert opinion or relevant quotes.

    **Additional Details:**  
    - Expand on the context, background, and importance.

    **Contact Information:**  
    - {contact_info}
    """

    # Generate press release
    response = model.generate_content(prompt)

    if response and hasattr(response, "text"):
        press_release_text = response.text.strip()
        press_release_chat = {
    "user_id": session["user_id"],
    "generator_type": "Press Release",
    "user_input": f"Press Type: {press_type}, Headline: {headline}",
    "ai_response": press_release_text[:1000],
    "timestamp": datetime.utcnow()
        }
        press_release_collection.insert_one(press_release_chat)
        generation_count=+1  
        print(generation_count)
        return jsonify({"press_release": press_release_text})

    return jsonify({"error": "AI could not generate a press release."}), 500


@app.route('/edit')
def edit_page():
    return render_template("edit.html")

@app.route("/edit-content", methods=["POST"])
def edit_content():
    """API to process user edits and regenerate content using AI."""
    if "user_id" not in session:
        return jsonify({"error": "Please log in to edit content."}), 403

    data = request.json
    user_edits = data.get("edited_content", "").strip()

    if not user_edits:
        return jsonify({"error": "No edited content provided!"}), 400

    # AI Prompt to refine user edits
    prompt = f"""
    You are an expert editor. Refine and improve the following user-edited content 
    while keeping the original meaning and enhancing clarity, grammar, and structure:

    **User Edits:** {user_edits}

    Return only the improved version.
    """

    try:
        # Send request to AI model
        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            improved_content = response.text.strip()
            session["edited_content"] = improved_content  # Store in session
            return jsonify({"improved_content": improved_content})

        return jsonify({"error": "AI failed to process the edit."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """Store AI feedback in the database for all AI generators."""
    data = request.json
    generator_name = data.get("generator_name")
    feedback_type = data.get("feedback_type")
    improvement_suggestion = data.get("improvement_suggestion")
    custom_feedback = data.get("custom_feedback")

    if not generator_name or not feedback_type:
        return jsonify({"error": "Missing required fields!"}), 400

    feedback_data = {
        "user_id": session.get("user_id"),
        "generator_name": generator_name,
        "feedback_type": feedback_type,
        "improvement_suggestion": improvement_suggestion,
        "custom_feedback": custom_feedback,
        "timestamp": datetime.utcnow()
    }

    feedback_collection.insert_one(feedback_data)
    return jsonify({"message": f"Feedback for {generator_name} submitted successfully!"})


@app.route("/admin/feedback")
def admin_feedback():
    """Admin page to view all AI feedback from all AI generators."""
    feedback_entries = list(feedback_collection.find().sort("timestamp", -1))
    return render_template("admin_feedback.html", feedback_entries=feedback_entries)

@app.route("/analyze-feedback", methods=["POST"])
def analyze_feedback():
    """AI analyzes feedback for all AI generators and improves responses."""
    data = request.json
    generator_name = data.get("generator_name")

    # Fetch feedback related to the specific AI generator
    feedback_entries = list(feedback_collection.find({"generator_name": generator_name}))

    if not feedback_entries:
        return jsonify({"message": f"No feedback found for {generator_name}."})

    # Combine feedback into a text prompt for AI analysis
    feedback_texts = [f"- {fb.improvement_suggestion}: {fb.custom_feedback}" for fb in feedback_entries]
    feedback_summary = "\n".join(feedback_texts)

    # AI Prompt to analyze feedback and improve content
    prompt = f"""
    Users provided the following feedback for the AI generator '{generator_name}':
    
    {feedback_summary}
    
    Based on this feedback, generate an improved version of the AI output.
    Ensure it aligns with the requested improvements and user expectations.
    """

    try:
        response = model.generate_content(prompt)  # AI processes feedback
        if response and hasattr(response, "text"):
            improved_content = response.text.strip()
            return jsonify({"improved_content": improved_content})
        return jsonify({"error": "AI failed to process feedback."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Function to get AI-generated content from the database
def get_original_content(feedback_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT generator, original_content, improvement FROM feedback WHERE id=?", (feedback_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else None

# Function to improve AI-generated content using Gemini AI
def improve_content(generator, content, improvement):
    model = genai.GenerativeModel("gemini-pro")  # Using Gemini Pro model

    prompt = f"Improve the following {generator} output by making it {improvement}:\n\n{content}"

    response = model.generate_content(prompt)

    return response.text.strip() if response else "Improvement failed."

# API to improve AI-generated content
@app.route("/improve_ai_content", methods=["POST"])
def improve_ai_content():
    data = request.json
    feedback_id = data.get("feedback_id")

    # Fetch the original content
    result = get_original_content(feedback_id)
    if not result:
        return jsonify({"error": "Feedback not found"}), 404

    generator, original_content, improvement = result

    # Generate improved content using Gemini AI
    improved_content = improve_content(generator, original_content, improvement)

    # Save improved content to the database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE feedback SET improved_content=? WHERE id=?", (improved_content, feedback_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "improved_content": improved_content})

# Connect to Database
def connect_db():
    return sqlite3.connect('hope_ai.db')

# Store Feedback
@app.route('/submit_feedback_v2', methods=['POST'])
def submit_feedback_v2():
    data = request.json
    generator_name = data['generator_name']
    feedback_type = data['feedback_type']
    improvement_area = data['improvement_area']
    comments = data['comments']
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (generator_name, feedback_type, improvement_area, comments, status, timestamp)
        VALUES (?, ?, ?, ?, 'Pending', datetime('now'))
    """, (generator_name, feedback_type, improvement_area, comments))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Feedback submitted successfully!"})

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
    
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)

@app.route("/edit-profile", methods=["POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form["name"]
    email = request.form["email"]

    users_collection.update_one(
        {"_id": ObjectId(session["user_id"])},
        {"$set": {"name": name, "email": email}}
    )

    # Update session variables after editing profile
    session["email"] = email
    session["name"] = name

    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile"))

@app.route("/change-password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("profile"))

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    # Debugging: Print stored password hash
    print(f"Stored password hash: {user['password']}")

    # Check if current password is correct
    if not bcrypt.check_password_hash(user["password"], current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("profile"))

    # Ensure new passwords match
    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("profile"))

    # Update password
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    users_collection.update_one(
        {"_id": ObjectId(session["user_id"])},
        {"$set": {"password": hashed_password}}
    )

    flash("Password changed successfully!", "success")
    return redirect(url_for("profile"))

@app.route("/chat-history-page")
def chat_history_page():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("chathistory.html")


@app.route("/get_chat_history", methods=["GET"])
@login_required
def get_chat_history():
    """Retrieve chat history for all AI generators from MongoDB"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    generator_type = request.args.get("generator_type", "").strip().lower()

    # Select the appropriate collection based on generator type
    collection_map = {
        "translation": translation_collection,
        "email generator": email_generator_collection,
        "proofreading": proofreading_collection,
        "story writing": story_writing_collection,
        "mobile marketing": mobile_marketing_collection,
        "seo": seo_collection,
        "youtube script": youtube_script_collection,
        "press release": press_release_collection,
        "website generator": website_generator_collection,
        "code optimizer": code_optimizer_collection,
        "blog": db["blog_chats"],  # ✅ Add Blog Generator
        "resume": db["resume_chats"],
        "ad_copy":db["ad_copy_chats"]
    }
    if generator_type == "all":
        chat_history = []
        for collection in collection_map.values():
            chat_history.extend(list(collection.find({"user_id": session["user_id"]}).sort("timestamp", -1)))
    elif generator_type in collection_map:
        chat_history = list(collection_map[generator_type].find({"user_id": session["user_id"]}).sort("timestamp", -1))
    else:
        return jsonify({"error": "Invalid generator type"}), 400
    

    # Convert ObjectId to string
    for chat in chat_history:
        chat["_id"] = str(chat["_id"])

    return jsonify({"chat_history": chat_history})


@app.route("/delete_chat/<chat_id>", methods=["DELETE"])
@login_required
def delete_chat(chat_id):
    """Delete a specific chat message based on chat ID"""

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Convert chat_id to ObjectId
        object_id = ObjectId(chat_id)

        # Find the chat entry in any AI generator collection
        collections = [
            translation_collection, email_generator_collection, proofreading_collection,
            story_writing_collection, mobile_marketing_collection, seo_collection,
            youtube_script_collection, press_release_collection, website_generator_collection,
            code_optimizer_collection
        ]

        deleted = False
        for collection in collections:
            result = collection.delete_one({"_id": object_id, "user_id": session["user_id"]})
            if result.deleted_count > 0:
                deleted = True
                break

        if deleted:
            return jsonify({"message": "Chat deleted successfully!"})
        else:
            return jsonify({"error": "Chat not found or unauthorized"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



@app.route("/generate", methods=["POST"])
def generate():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    redirect_response = track_generations()
    if redirect_response:
        return redirect_response  # Redirect to Pricing Page after 5 generations
    
    return "AI Generation Successful"  # Replace with actual AI generation logic
def count():
    generation_count=+1
    print(generation_count)
@app.route("/logout")
def logout():
    session.pop("user_id",None)
    session.pop('google_token', None)
    logout_user()
    return redirect(url_for("login"))
    
if __name__ =='__main__':
    app.run(debug=True)


