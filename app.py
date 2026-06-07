from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from utils.parser import get_text
from flask import redirect

import bcrypt
import os

app = Flask(__name__)
CORS(app)

# MongoDB Connection
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["resumeDB"]
users = db["users"]


@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/signuppage")
def signup_page():
    return render_template("signup.html")


@app.route("/uploadpage")
def upload_page():
    return render_template("upload.html")

# Upload Folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Skills List
skills_list = [
    "python",
    "java",
    "c++",
    "javascript",
    "react",
    "node",
    "mongodb",
    "flask",
    "html",
    "css",
    "sql"
]


# Skill Matching

def match_skills(text):

    found = []
    text = text.lower()

    for skill in skills_list:
        if skill in text:
            found.append(skill)

    return found


# Resume Score

def calculate_score(text, skills):

    score = 0

    score += min(len(skills) * 8, 40)

    text = text.lower()

    if "project" in text:
        score += 15

    if "experience" in text:
        score += 15

    if "github" in text:
        score += 10

    if "linkedin" in text:
        score += 10

    if "certification" in text:
        score += 10

    if score > 100:
        score = 100

    return score


# Suggestions

def generate_suggestions(text, skills):

    suggestions = []

    text = text.lower()

    if len(skills) < 5:
        suggestions.append(
            "Add more technical skills relevant to your domain."
        )

    if "project" not in text:
        suggestions.append(
            "Add a Projects section with 2-3 major projects."
        )

    if "experience" not in text:
        suggestions.append(
            "Add internship or work experience."
        )

    if "github" not in text:
        suggestions.append(
            "Include your GitHub profile."
        )

    if "linkedin" not in text:
        suggestions.append(
            "Include your LinkedIn profile."
        )

    if "certification" not in text:
        suggestions.append(
            "Add certifications and courses."
        )

    if "objective" not in text:
        suggestions.append(
            "Add a short career objective."
        )

    if len(suggestions) == 0:
        suggestions.append(
            "Excellent resume. No major improvements detected."
        )

    return suggestions


@app.route("/")
def home():
    return render_template("index.html")

# Signup
@app.route("/signup", methods=["POST"])
def signup():

    data = request.json

    existing_user = users.find_one({"email": data["email"]})

    if existing_user:
        return jsonify({"message": "User already exists"})

    hashed = bcrypt.hashpw(
        data["password"].encode("utf-8"),
        bcrypt.gensalt()
    )

    users.insert_one({
        "email": data["email"],
        "password": hashed
    })

    return jsonify({"message": "User registered successfully"})
    # Login
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    user = users.find_one({"email": data["email"]})

    if not user:
        return jsonify({"message": "User not found"})

    if bcrypt.checkpw(
        data["password"].encode("utf-8"),
        user["password"]
    ):
        return jsonify({"message": "Login successful"})

    return jsonify({"message": "Wrong password"})
    # Resume Upload & Analysis
@app.route("/upload", methods=["POST"])
def upload_resume():

    file = request.files["resume"]

    filename = secure_filename(file.filename)

    path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(path)

    text = get_text(path)

    skills = match_skills(text)

    score = calculate_score(text, skills)

    suggestions = generate_suggestions(text, skills)
    return jsonify({
        "message": "Resume uploaded successfully",
        "skills": skills,
        "score": score,
        "suggestions": suggestions,
        "preview": text[:1000]
    })


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)