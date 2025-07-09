from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import uuid4
from statistics import mean
from datetime import datetime
from passlib.hash import bcrypt
from backend.mongo import sessions, users
from backend.scoring_engine import score_candidate_answer
from backend.behavioral_adjuster import detect_tone_and_suggest_style
from backend.feedback_generator import generate_feedback
from fastapi import UploadFile, File
from backend.profile_comparator import compare_resume_to_jd
import fitz  # PyMuPDF
from backend.question_generator import generate_followup_question
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

allowed_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION = {}

class AnswerRequest(BaseModel):
    answer: str
    session_id: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/signup")
def signup(user: UserCreate):
    if users.find_one({"email": user.email}):
        return {"error": "User already exists"}
    hashed_pw = bcrypt.hash(user.password)
    users.insert_one({"email": user.email, "password": hashed_pw})
    return {"message": "Signup successful"}

@app.post("/auth/login")
def login(user: UserLogin):
    existing = users.find_one({"email": user.email})
    if not existing:
        return {"error": "User not found"}
    if not bcrypt.verify(user.password, existing["password"]):
        return {"error": "Incorrect password"}
    return {"message": "Login successful", "user_id": str(existing["_id"])}

@app.post("/interview/start")
def start_interview():
    session_id = str(uuid4())
    SESSION[session_id] = {
        "index": 0,
        "answers": [],
        "scores": [],
        "tone_feedback": [],
        "transcript": [],
    }
    intro = "Welcome to your personalized interview session. Let’s begin."
    first_question = "Can you describe a recent project you're proud of?"
    SESSION[session_id]["transcript"].append({"question": first_question})
    return {
        "question": first_question,
        "intro": intro,
        "session_id": session_id
    }

@app.post("/interview/next")
def next_question(payload: AnswerRequest):
    sid = payload.session_id
    data = SESSION[sid]
    idx = data["index"]
    last_q = data["transcript"][idx]["question"]

    data["answers"].append(payload.answer)
    data["transcript"][idx]["answer"] = payload.answer

    score = score_candidate_answer(last_q, payload.answer)
    data["scores"].append(score)

    tone = detect_tone_and_suggest_style(payload.answer)
    data["tone_feedback"].append(tone)

    feedback = generate_feedback(last_q, payload.answer)
    next_q = generate_followup_question(last_q, payload.answer)

    data["index"] += 1
    data["transcript"].append({"question": next_q})

    return {
        "question": next_q,
        "feedback": feedback,
        "tone": tone,
        "score": score
    }

@app.get("/interview/summary/{session_id}")
def interview_summary(session_id: str, user_email: Optional[str] = Query(None)):
    data = SESSION.get(session_id, {})
    scores = data.get("scores", [])
    transcript = data.get("transcript", [])

    avg_score = {
        "clarity": round(mean(s["clarity"] for s in scores if "clarity" in s), 2),
        "technical_depth": round(mean(s["technical_depth"] for s in scores if "technical_depth" in s), 2),
        "relevance": round(mean(s["relevance"] for s in scores if "relevance" in s), 2),
        "confidence": round(mean(s["confidence"] for s in scores if "confidence" in s), 2),
    }

    summary = {
        "session_id": session_id,
        "user_email": user_email,
        "transcript": transcript,
        "average_score": avg_score,
        "recommendation": "Strong candidate" if avg_score["clarity"] >= 4 else "Needs improvement",
        "created_at": datetime.utcnow()
    }

    sessions.insert_one(summary)
    return summary

@app.get("/sessions/{user_email}")
def get_user_sessions(user_email: str):
    results = list(sessions.find({"user_email": user_email}))
    for r in results:
        r["_id"] = str(r["_id"])
    return results


@app.post("/upload/resume-jd")
async def upload_files(resume: UploadFile = File(...), jd: UploadFile = File(...)):
    def extract_text(file: UploadFile):
        content = file.file.read()
        doc = fitz.open("pdf", content)
        text = "\n".join(page.get_text() for page in doc)
        return text

    resume_text = extract_text(resume)
    jd_text = extract_text(jd)

    result = compare_resume_to_jd(resume_text, jd_text)
    return result
