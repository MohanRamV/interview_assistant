from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import uuid4
from statistics import mean
from datetime import datetime
from passlib.hash import bcrypt
from backend.scoring_engine import score_candidate_answer
from backend.feedback_generator import generate_feedback
from backend.interview_evaluator import evaluator
from fastapi import UploadFile, File
from backend.profile_comparator import compare_resume_to_jd
from backend.question_generator import generate_dynamic_question
from backend.gemini_resume_parser import parse_resume_with_gemini
from backend.jd_analyzer import analyze_job_description
from backend.mongo import sessions, users, parsed_resumes, parsed_jds

import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
import hashlib

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

def generate_file_hash(content: bytes) -> str:
    """Generate a hash for file content to identify duplicates."""
    return hashlib.md5(content).hexdigest()

def get_or_parse_resume(resume_content: bytes, resume_raw: str):
    """Get parsed resume from DB or parse and save it."""
    file_hash = generate_file_hash(resume_content)
    
    # Check if already parsed
    existing = parsed_resumes.find_one({"file_hash": file_hash})
    if existing:
        print(f"Using cached resume data for hash: {file_hash}")
        return existing["parsed_data"]
    
    # Parse and save
    print(f"Parsing new resume, hash: {file_hash}")
    parsed_data = parse_resume_with_gemini(resume_raw)
    
    # Save to database
    parsed_resumes.insert_one({
        "file_hash": file_hash,
        "parsed_data": parsed_data,
        "created_at": datetime.utcnow()
    })
    
    return parsed_data

def get_or_parse_jd(jd_content: bytes, jd_raw: str):
    """Get parsed JD from DB or parse and save it."""
    file_hash = generate_file_hash(jd_content)
    
    # Check if already parsed
    existing = parsed_jds.find_one({"file_hash": file_hash})
    if existing:
        print(f"Using cached JD data for hash: {file_hash}")
        return existing["parsed_data"]
    
    # Parse and save
    print(f"Parsing new JD, hash: {file_hash}")
    parsed_data = analyze_job_description(jd_raw)
    
    # Save to database
    parsed_jds.insert_one({
        "file_hash": file_hash,
        "parsed_data": parsed_data,
        "created_at": datetime.utcnow()
    })
    
    return parsed_data

def generate_interview_greeting(resume_text: str, jd_text: str) -> str:
    """
    Generate a personalized greeting with company and job role information.
    """
    try:
        # Create a hash for the resume + JD combination
        combined_text = resume_text[:500] + jd_text[:500]
        greeting_hash = hashlib.md5(combined_text.encode()).hexdigest()
        
        # Check if greeting already exists in session cache
        if hasattr(generate_interview_greeting, 'greeting_cache'):
            if greeting_hash in generate_interview_greeting.greeting_cache:
                print(f"Using cached greeting for hash: {greeting_hash}")
                return generate_interview_greeting.greeting_cache[greeting_hash]
        else:
            generate_interview_greeting.greeting_cache = {}
        
        from backend.llm_client import model
        
        prompt = f"""You are an AI assistant that generates interview greetings. Generate ONLY the greeting text, no explanations or labels.

Create a brief, welcoming interview introduction (2-3 sentences) that includes:
1. A warm greeting
2. The company name (extract from JD)
3. The job role/position
4. Brief explanation of the interview format (4 questions, different types)

Resume: {resume_text[:500]}...
Job Description: {jd_text[:500]}...

Output ONLY the greeting text. Do not include any labels, explanations, or formatting."""

        response = model.generate_content(prompt)
        greeting = response.text.strip()
        
        # Clean up the response to remove any prompt artifacts
        if greeting.startswith("Here's a brief"):
            # Remove common prompt artifacts
            lines = greeting.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith("Here's") and not line.startswith("Generate") and not line.startswith("Create"):
                    greeting = '\n'.join(lines[i:])
                    break
        
        if not greeting or len(greeting) < 20:
            greeting = "Welcome to your interview! We'll be asking you 4 questions covering different aspects of your experience and skills. Let's begin!"
        
        # Cache the greeting
        generate_interview_greeting.greeting_cache[greeting_hash] = greeting
        
        return greeting
    except Exception as e:
        print(f"Greeting generation error: {e}")
        return "Welcome to your interview! We'll be asking you 4 questions covering different aspects of your experience and skills. Let's begin!"

class AnswerRequest(BaseModel):
    answer: str
    session_id: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TabSwitchRequest(BaseModel):
    session_id: str
    tab_switch_count: int

class SecurityMetricsRequest(BaseModel):
    session_id: str
    tab_switch_count: int
    fullscreen_used: bool
    interview_duration_minutes: int

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

@app.post("/upload/resume-jd")
async def upload_files(resume: UploadFile = File(...), jd: UploadFile = File(...), user_email: str = ""):
    try:
        import time
        def extract_text(file: UploadFile):
            file.file.seek(0)
            content = file.file.read()
            doc = fitz.open("pdf", content)
            return "\n".join(page.get_text() for page in doc)  # type: ignore

        # Extract text from uploaded files
        resume.file.seek(0)
        resume_raw = extract_text(resume)
        jd.file.seek(0)
        jd_raw = extract_text(jd)

        # Log extracted text lengths for debugging
        print(f"[UPLOAD] Extracted resume text length: {len(resume_raw)}")
        print(f"[UPLOAD] Extracted JD text length: {len(jd_raw)}")

        # If either text is empty, return a clear error
        if not resume_raw or not resume_raw.strip():
            return {"error": "Resume text could not be extracted from the uploaded file. Please check your file and try again."}
        if not jd_raw or not jd_raw.strip():
            return {"error": "Job description text could not be extracted from the uploaded file. Please check your file and try again."}

        # Reset file pointers for hashing
        resume.file.seek(0)
        resume_content = resume.file.read()
        jd.file.seek(0)
        jd_content = jd.file.read()

        # Use cached parsing or parse and cache
        parsed_resume = get_or_parse_resume(resume_content, resume_raw)
        time.sleep(0.3)  # 300ms delay
        parsed_jd = get_or_parse_jd(jd_content, jd_raw)
        time.sleep(0.3)  # 300ms delay

        # Compare resume to JD (skills analysis)
        result = compare_resume_to_jd(resume_raw, jd_raw)

        # Create new session
        new_session_id = str(uuid4())
        SESSION[new_session_id] = {
            "index": 0,
            "answers": [],
            "scores": [],
            "tone_feedback": [],
            "transcript": [],
            "resume_text": resume_raw,
            "jd_text": jd_raw,
            "question_types": [
                "resume-based",
                "job-description-based", 
                "follow-up",
                "behavioral"
            ],
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "resume_jd_summary": result.get("summary", ""),
            "parsed_resume": parsed_resume,
            "parsed_jd": parsed_jd,
            "user_email": user_email  # Store user email in session
        }

        return {
            "session_id": new_session_id,
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "summary": result.get("summary", ""),
            "parsed_resume": parsed_resume,
            "parsed_jd": parsed_jd
        }
    except Exception as e:
        print(f"[UPLOAD] Exception: {e}")
        return {"error": f"Failed to process files: {str(e)}"}

@app.post("/interview/start")
async def start_interview(request: Request):
    try:
        payload = await request.json()
        session_id = payload.get("session_id")

        print(f"Interview start called for session: {session_id}")

        if not session_id or session_id not in SESSION:
            return {"error": "Invalid session_id"}

        # Check if interview has already started
        if SESSION[session_id].get("interview_started", False):
            print(f"Interview already started for session: {session_id}")
            # Return the existing first question
            if SESSION[session_id]["transcript"]:
                return {
                    "session_id": session_id,
                    "question": SESSION[session_id]["transcript"][0]["question"],
                    "greeting": SESSION[session_id].get("greeting", "Welcome to your interview!")
                }

        # Validate that we have resume and JD text to prevent hallucination
        resume_text = SESSION[session_id].get("resume_text", "")
        jd_text = SESSION[session_id].get("jd_text", "")
        
        if not resume_text or not resume_text.strip():
            print(f"WARNING: Session {session_id} has no resume text - this may cause hallucination")
            return {"error": "Cannot start interview: Resume information is missing. Please upload a resume first."}
        
        if not jd_text or not jd_text.strip():
            print(f"WARNING: Session {session_id} has no job description text - this may cause hallucination")
            return {"error": "Cannot start interview: Job description information is missing. Please upload a job description first."}

        # Initialize session for interview
        SESSION[session_id]["index"] = 0
        SESSION[session_id]["transcript"] = []
        SESSION[session_id]["interview_started"] = True

        # Generate personalized greeting
        greeting = generate_interview_greeting(resume_text, jd_text)
        SESSION[session_id]["greeting"] = greeting

        # Add delay between API calls to prevent rate limiting
        import time
        time.sleep(0.5)  # 500ms delay

        # Generate first question
        question_type = SESSION[session_id]["question_types"][0]
        first_q = generate_dynamic_question(
            resume_text,
            jd_text,
            [],
            question_type
        )

        print(f"Generated first question for session {session_id}: {first_q[:50]}...")

        # Save first question in transcript
        SESSION[session_id]["transcript"].append({"question": first_q})

        return {
            "session_id": session_id,
            "question": first_q,
            "greeting": greeting
        }
    except Exception as e:
        print(f"Error generating greeting: {e}")
        return "Welcome to your interview! We'll be asking you 4 questions covering different aspects of your experience and skills. Let's begin!"

@app.post("/interview/next")
async def next_question(payload: AnswerRequest):
    try:
        sid = payload.session_id
        if sid not in SESSION:
            return {"error": "Invalid session_id"}

        data = SESSION[sid]
        idx = data["index"]
        
        print(f"Processing answer for session {sid}, current index: {idx}, total questions: {len(data['question_types'])}")
        
        if idx >= len(data["question_types"]):
            print(f"Interview completed for session {sid} - index {idx} >= {len(data['question_types'])}")
            return {"question": "", "message": "Interview completed"}

        # Get current question type
        qtype = data["question_types"][idx]
        print(f"Current question type: {qtype}")

        # Save the answer (no scoring here - will be done at summary)
        last_q = data["transcript"][idx]["question"]
        data["answers"].append(payload.answer)
        data["transcript"][idx]["answer"] = payload.answer

        # Generate next question if there are more questions
        if idx + 1 < len(data["question_types"]):
            print(f"Generating next question for session {sid}, type: {data['question_types'][idx + 1]}")
            import time
            start_time = time.time()
            
            next_q = generate_dynamic_question(
                resume_text=data["resume_text"],
                jd_text=data["jd_text"],
                transcript=data["transcript"],
                question_type=data["question_types"][idx + 1]
            )
            
            generation_time = time.time() - start_time
            print(f"Question generation took {generation_time:.2f} seconds for session {sid}")
            
            data["transcript"].append({"question": next_q})
            data["index"] += 1
            print(f"Generated next question for session {sid}, new index: {data['index']}")
            return {
                "question": next_q
            }

        # Interview completed - ensure we have all 4 questions answered
        if len(data["answers"]) < 4:
            print(f"Warning: Interview completing with only {len(data['answers'])} answers for session {sid}")
        
        data["index"] += 1
        print(f"Interview completed for session {sid} - no more questions")
        return {
            "question": "",
            "message": "Interview completed"
        }
    except Exception as e:
        print(f"Error in next_question: {e}")
        return {"error": f"Failed to process answer: {str(e)}"}

@app.post("/interview/tab-switch")
async def track_tab_switch(payload: TabSwitchRequest):
    try:
        sid = payload.session_id
        if sid not in SESSION:
            return {"error": "Invalid session_id"}

        data = SESSION[sid]
        data["tab_switch_count"] = payload.tab_switch_count
        return {"message": "Tab switch count updated"}
    except Exception as e:
        return {"error": f"Failed to update tab switch count: {str(e)}"}

@app.post("/interview/security-metrics")
async def store_security_metrics(payload: SecurityMetricsRequest):
    try:
        sid = payload.session_id
        if sid not in SESSION:
            return {"error": "Invalid session_id"}

        data = SESSION[sid]
        data["tab_switch_count"] = payload.tab_switch_count
        data["fullscreen_used"] = payload.fullscreen_used
        data["interview_duration_minutes"] = payload.interview_duration_minutes
        
        print(f"Security metrics stored for session {sid}:")
        print(f"  - Tab switches: {payload.tab_switch_count}")
        print(f"  - Fullscreen used: {payload.fullscreen_used}")
        print(f"  - Duration: {payload.interview_duration_minutes} minutes")
        
        return {"message": "Security metrics stored successfully"}
    except Exception as e:
        return {"error": f"Failed to store security metrics: {str(e)}"}

@app.get("/interview/summary/{session_id}")
def interview_summary(session_id: str, user_email: Optional[str] = Query(None)):
    try:
        data = SESSION.get(session_id, {})
        if not data:
            # Try to find session in database if not in memory
            from bson import ObjectId
            session_data = None
            try:
                object_id = ObjectId(session_id)
                session_data = sessions.find_one({"_id": object_id})
            except Exception:
                session_data = sessions.find_one({"session_id": session_id})
            
            if session_data:
                data = session_data
                print(f"Found session {session_id} in database, using that data")
            else:
                return {"error": "Session not found in memory or database"}

        # Check if summary already exists in database
        existing_summary = sessions.find_one({"session_id": session_id})
        if existing_summary:
            print(f"Summary already exists for session {session_id}, returning existing summary")
            existing_summary["_id"] = str(existing_summary["_id"])
            return existing_summary

        transcript = data.get("transcript", [])

        # Use user_email from session if not provided
        if not user_email:
            user_email = data.get("user_email")

        # Ensure we have skills data
        matched_skills = data.get("matched_skills", [])
        missing_skills = data.get("missing_skills", [])
        resume_jd_summary = data.get("resume_jd_summary", "")
        
        # If skills analysis is missing, try to regenerate it
        if not matched_skills and not missing_skills:
            resume_text = data.get("resume_text", "")
            jd_text = data.get("jd_text", "")
            if resume_text and jd_text:
                print(f"Regenerating skills analysis for session {session_id}")
                skills_result = compare_resume_to_jd(resume_text, jd_text)
                matched_skills = skills_result.get("matched_skills", [])
                missing_skills = skills_result.get("missing_skills", [])
                resume_jd_summary = skills_result.get("summary", "")
                print(f"Regenerated skills: {len(matched_skills)} matched, {len(missing_skills)} missing")

        # Calculate all scoring, tone analysis, and feedback at once
        scores = []
        enhanced_transcript = []
        
        for i, item in enumerate(transcript):
            enhanced_item = item.copy()
            if "answer" in item:  # Only process completed Q&A pairs
                try:
                    # Score the answer
                    score = score_candidate_answer(item["question"], item["answer"])
                    scores.append(score)
                    
                    # Generate feedback
                    feedback = generate_feedback(item["question"], item["answer"])
                    enhanced_item["feedback"] = feedback
                    
                    # Note: Tone analysis removed as it's not being used
                    
                except Exception as e:
                    print(f"Failed to process Q&A {i}: {e}")
                    # Use default scores and feedback
                    default_score = {
                        "clarity": 3,
                        "relevance": 3,
                        "technical_depth": 3,
                        "confidence": 3,
                        "comment": "Processing failed - using default values"
                    }
                    scores.append(default_score)
                    enhanced_item["feedback"] = "Feedback generation failed."
            enhanced_transcript.append(enhanced_item)

        # Calculate average scores
        if scores:
            avg_score = {
                "clarity": round(mean(s.get("clarity", 0) for s in scores), 2),
                "technical_depth": round(mean(s.get("technical_depth", 0) for s in scores), 2),
                "relevance": round(mean(s.get("relevance", 0) for s in scores), 2),
                "confidence": round(mean(s.get("confidence", 0) for s in scores), 2),
            }

            # Calculate overall score
            overall_score = (avg_score["clarity"] + avg_score["relevance"] + avg_score["technical_depth"] + avg_score["confidence"]) / 4
        else:
            avg_score = {"clarity": 0, "technical_depth": 0, "relevance": 0, "confidence": 0}
            overall_score = 0

        # Generate recommendation based on scores
        if overall_score >= 4.5:
            recommendation = "Exceptional candidate - Highly recommended"
        elif overall_score >= 4.0:
            recommendation = "Strong candidate - Recommended"
        elif overall_score >= 3.5:
            recommendation = "Good candidate - Consider for role"
        elif overall_score >= 3.0:
            recommendation = "Average candidate - Needs improvement"
        elif overall_score >= 2.5:
            recommendation = "Below average - Significant improvement needed"
        else:
            recommendation = "Poor performance - Not recommended"

        summary = {
            "session_id": session_id,
            "user_email": user_email,
            "transcript": enhanced_transcript,  # Use enhanced transcript with feedback
            "average_score": avg_score,
            "overall_score": round(overall_score, 2),
            "recommendation": recommendation,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "resume_jd_summary": resume_jd_summary,
            "resume_text": data.get("resume_text", ""),  # Include resume text for evaluation
            "jd_text": data.get("jd_text", ""),  # Include JD text for evaluation
            "parsed_resume": data.get("parsed_resume", {}),
            "parsed_jd": data.get("parsed_jd", {}),
            "security_metrics": {
                "tab_switch_count": data.get("tab_switch_count", 0),
                "fullscreen_used": data.get("fullscreen_used", False),
                "interview_duration_minutes": data.get("interview_duration_minutes", 0)
            },
            "created_at": datetime.utcnow()
        }

        # Save to database
        print(f"Saving new summary for session {session_id} with {len(matched_skills)} matched skills")
        result = sessions.insert_one(summary)
        summary["_id"] = str(result.inserted_id)  # 🛠️ convert ObjectId to string
        return summary
    except Exception as e:
        return {"error": f"Failed to generate summary: {str(e)}"}

@app.get("/user/data/{user_email}")
def get_user_data(user_email: str):
    """
    Get the most recent parsed resume and JD data for a user.
    """
    try:
        # Get the most recent session for this user (always use latest)
        latest_session = sessions.find_one(
            {"user_email": user_email},
            sort=[("created_at", -1)]  # Most recent first
        )
        
        if not latest_session:
            return {"error": "No data found for user"}
        
        # Return the parsed data
        return {
            "_id": str(latest_session["_id"]),
            "resume_filename": "Previous Resume",
            "jd_filename": "Previous Job Description", 
            "matched_skills": latest_session.get("matched_skills", []),
            "missing_skills": latest_session.get("missing_skills", []),
            "resume_jd_summary": latest_session.get("resume_jd_summary", ""),
            "parsed_resume": latest_session.get("parsed_resume", {}),
            "parsed_jd": latest_session.get("parsed_jd", {}),
            "updated_at": latest_session.get("created_at", datetime.utcnow())
        }
    except Exception as e:
        return {"error": f"Failed to fetch user data: {str(e)}"}

@app.post("/create-session-from-existing")
async def create_session_from_existing(request: Request):
    """
    Create a new interview session using existing parsed data.
    """
    try:
        payload = await request.json()
        user_email = payload.get("user_email")
        existing_data_id = payload.get("existing_data_id")
        
        if not user_email or not existing_data_id:
            return {"error": "Missing user_email or existing_data_id"}
        
        # Try to find existing session by ObjectId first, then by session_id
        from bson import ObjectId
        existing_session = None
        try:
            object_id = ObjectId(existing_data_id)
            existing_session = sessions.find_one({"_id": object_id})
        except Exception:
            # If not ObjectId, try as UUID string
            existing_session = sessions.find_one({"session_id": existing_data_id})
        
        if not existing_session:
            return {"error": "Existing session not found"}
        
        # Create new session with existing data
        new_session_id = str(uuid4())
        
        # Ensure we have the essential data
        resume_text = existing_session.get("resume_text", "")
        jd_text = existing_session.get("jd_text", "")
        
        # If skills analysis is missing or empty, regenerate it
        matched_skills = existing_session.get("matched_skills", [])
        missing_skills = existing_session.get("missing_skills", [])
        resume_jd_summary = existing_session.get("resume_jd_summary", "")
        
        if not matched_skills and not missing_skills and resume_text and jd_text:
            print(f"Regenerating skills analysis for new session from existing data")
            skills_result = compare_resume_to_jd(resume_text, jd_text)
            matched_skills = skills_result.get("matched_skills", [])
            missing_skills = skills_result.get("missing_skills", [])
            resume_jd_summary = skills_result.get("summary", "")
        
        # Create session data for both in-memory and MongoDB
        session_data = {
            "session_id": new_session_id,
            "user_email": user_email,
            "index": 0,
            "answers": [],
            "scores": [],
            "tone_feedback": [],
            "transcript": [],
            "resume_text": resume_text,
            "jd_text": jd_text,
            "question_types": [
                "resume-based",
                "job-description-based", 
                "follow-up",
                "behavioral"
            ],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "resume_jd_summary": resume_jd_summary,
            "parsed_resume": existing_session.get("parsed_resume", {}),
            "parsed_jd": existing_session.get("parsed_jd", {}),
            "created_at": datetime.utcnow()
        }
        
        # Store in MongoDB
        result = sessions.insert_one(session_data)
        
        # Also store in in-memory session for active interview
        SESSION[new_session_id] = session_data
        
        print(f"Created new session {new_session_id} from existing data with {len(matched_skills)} matched skills")
        
        return {
            "session_id": new_session_id,
            "message": "Session created from existing data",
            "matched_skills_count": len(matched_skills),
            "missing_skills_count": len(missing_skills)
        }
    except Exception as e:
        return {"error": f"Failed to create session: {str(e)}"}

@app.get("/sessions/{user_email}")
def get_user_sessions(user_email: str):
    try:
        # Get sessions sorted by creation date (newest first) to match cleanup logic
        results = list(sessions.find({"user_email": user_email}).sort("created_at", -1))
        for r in results:
            r["_id"] = str(r["_id"])
        return results
    except Exception as e:
        return {"error": f"Failed to fetch sessions: {str(e)}"}

@app.post("/evaluate/interview/{session_id}")
def evaluate_interview_quality(session_id: str):
    """
    Evaluate the quality, consistency, and reliability of an interview session.
    """
    try:
        from bson import ObjectId
        
        # Try to find session by ObjectId first, then by session_id
        session_data = None
        try:
            object_id = ObjectId(session_id)
            session_data = sessions.find_one({"_id": object_id})
        except Exception:
            # If not ObjectId, try as UUID string
            session_data = sessions.find_one({"session_id": session_id})
        
        if not session_data:
            return {"error": "Session not found"}
        
        # Convert ObjectId to string for JSON serialization
        session_data["_id"] = str(session_data["_id"])
        
        # Run comprehensive evaluation
        evaluation_result = evaluator.run_comprehensive_evaluation(session_data)
        
        # Save evaluation to database
        evaluation_result["session_id"] = session_data.get("session_id", session_id)
        evaluation_result["created_at"] = datetime.utcnow()
        
        # Store in a separate collection for evaluations
        from backend.mongo import db
        evaluations = db["interview_evaluations"]
        result = evaluations.insert_one(evaluation_result)
        evaluation_result["_id"] = str(result.inserted_id)
        
        return {
            "message": "Evaluation completed successfully",
            "evaluation": evaluation_result
        }
    except Exception as e:
        return {"error": f"Evaluation failed: {str(e)}"}

@app.get("/evaluations/{session_id}")
def get_interview_evaluation(session_id: str):
    """
    Get evaluation results for a specific interview session.
    """
    try:
        from backend.mongo import db
        from bson import ObjectId
        evaluations = db["interview_evaluations"]
        
        # Try to find evaluation by ObjectId first, then by session_id
        evaluation = None
        try:
            object_id = ObjectId(session_id)
            evaluation = evaluations.find_one({"session_id": str(object_id)})
        except Exception:
            # If not ObjectId, try as UUID string
            evaluation = evaluations.find_one({"session_id": session_id})
        
        if evaluation:
            evaluation["_id"] = str(evaluation["_id"])
            return evaluation
        else:
            return {"error": "Evaluation not found"}
    except Exception as e:
        return {"error": f"Failed to fetch evaluation: {str(e)}"}

@app.post("/regenerate-skills/{session_id}")
def regenerate_skills_analysis(session_id: str):
    """
    Regenerate skills analysis for an existing session.
    """
    try:
        from bson import ObjectId
        
        # Try to find session by ObjectId first, then by session_id
        session_data = None
        try:
            object_id = ObjectId(session_id)
            session_data = sessions.find_one({"_id": object_id})
        except Exception:
            # If not ObjectId, try as UUID string
            session_data = sessions.find_one({"session_id": session_id})
        
        if not session_data:
            return {"error": "Session not found"}
        
        # Get resume and JD text
        resume_text = session_data.get("resume_text", "")
        jd_text = session_data.get("jd_text", "")
        
        if not resume_text or not jd_text:
            return {"error": "Resume or JD text not found in session"}
        
        # Regenerate skills analysis
        print(f"Regenerating skills analysis for session {session_id}")
        skills_result = compare_resume_to_jd(resume_text, jd_text)
        
        # Update the session with new skills data
        update_query = {"_id": session_data["_id"]} if "_id" in session_data else {"session_id": session_id}
        sessions.update_one(
            update_query,
            {
                "$set": {
                    "matched_skills": skills_result.get("matched_skills", []),
                    "missing_skills": skills_result.get("missing_skills", []),
                    "resume_jd_summary": skills_result.get("summary", ""),
                    "skills_updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Skills analysis regenerated successfully",
            "matched_skills": skills_result.get("matched_skills", []),
            "missing_skills": skills_result.get("missing_skills", []),
            "summary": skills_result.get("summary", "")
        }
        
    except Exception as e:
        return {"error": f"Failed to regenerate skills analysis: {str(e)}"}

@app.get("/debug/session/{session_id}")
def debug_session_data(session_id: str):
    """
    Debug endpoint to check what data is stored in a session.
    """
    try:
        from bson import ObjectId
        
        # Try to find session by ObjectId first, then by session_id
        session_data = None
        try:
            object_id = ObjectId(session_id)
            session_data = sessions.find_one({"_id": object_id})
        except Exception:
            # If not ObjectId, try as UUID string
            session_data = sessions.find_one({"session_id": session_id})
        
        if not session_data:
            return {"error": "Session not found"}
        
        # Convert ObjectId to string for JSON serialization
        session_data["_id"] = str(session_data["_id"])
        
        # Check if datetime objects need conversion
        if "created_at" in session_data:
            session_data["created_at"] = session_data["created_at"].isoformat()
        
        return {
            "session_id": session_id,
            "has_resume_text": bool(session_data.get("resume_text")),
            "has_jd_text": bool(session_data.get("jd_text")),
            "resume_text_length": len(session_data.get("resume_text", "")),
            "jd_text_length": len(session_data.get("jd_text", "")),
            "matched_skills": session_data.get("matched_skills", []),
            "missing_skills": session_data.get("missing_skills", []),
            "matched_skills_count": len(session_data.get("matched_skills", [])),
            "missing_skills_count": len(session_data.get("missing_skills", [])),
            "has_transcript": bool(session_data.get("transcript")),
            "transcript_length": len(session_data.get("transcript", [])),
            "has_scores": bool(session_data.get("scores")),
            "scores_count": len(session_data.get("scores", [])),
            "overall_score": session_data.get("overall_score", "Not calculated"),
            "average_score": session_data.get("average_score", "Not calculated"),
            "created_at": session_data.get("created_at"),
            "user_email": session_data.get("user_email")
        }
    except Exception as e:
        return {"error": f"Debug failed: {str(e)}"}

@app.post("/debug/test-skills-matching")
async def test_skills_matching(request: Request):
    """
    Test endpoint to debug skills matching with sample data.
    """
    try:
        payload = await request.json()
        resume_text = payload.get("resume_text", "")
        jd_text = payload.get("jd_text", "")
        
        if not resume_text or not jd_text:
            return {"error": "Both resume_text and jd_text are required"}
        
        # Test skills matching
        skills_result = compare_resume_to_jd(resume_text, jd_text)
        
        return {
            "matched_skills": skills_result.get("matched_skills", []),
            "missing_skills": skills_result.get("missing_skills", []),
            "summary": skills_result.get("summary", ""),
            "error": skills_result.get("error", ""),
            "matched_count": len(skills_result.get("matched_skills", [])),
            "missing_count": len(skills_result.get("missing_skills", []))
        }
    except Exception as e:
        return {"error": f"Test failed: {str(e)}"}

@app.post("/debug/test-scoring")
async def test_scoring(request: Request):
    """
    Test endpoint to debug scoring with sample Q&A.
    """
    try:
        payload = await request.json()
        question = payload.get("question", "")
        answer = payload.get("answer", "")
        
        if not question or not answer:
            return {"error": "Both question and answer are required"}
        
        # Test scoring
        score_result = score_candidate_answer(question, answer)
        
        return {
            "clarity": score_result.get("clarity", 0),
            "relevance": score_result.get("relevance", 0),
            "technical_depth": score_result.get("technical_depth", 0),
            "confidence": score_result.get("confidence", 0),
            "comment": score_result.get("comment", ""),
            "average_score": (score_result.get("clarity", 0) + score_result.get("relevance", 0) + 
                            score_result.get("technical_depth", 0) + score_result.get("confidence", 0)) / 4
        }
    except Exception as e:
        return {"error": f"Test failed: {str(e)}"}

@app.post("/cleanup-sessions/{user_email}")
def cleanup_old_sessions(user_email: str):
    """
    Clean up old sessions and keep only the 6 most recent ones for a user.
    """
    try:
        # Get all sessions for this user, sorted by creation date (newest first)
        all_sessions = list(sessions.find(
            {"user_email": user_email}
        ).sort("created_at", -1))
        
        if len(all_sessions) <= 6:
            return {
                "message": f"No cleanup needed. User has {len(all_sessions)} sessions (≤ 6 limit)",
                "sessions_kept": len(all_sessions),
                "sessions_deleted": 0
            }
        
        # Keep the 6 most recent sessions
        sessions_to_keep = all_sessions[:6]
        sessions_to_delete = all_sessions[6:]
        
        # Delete old sessions
        deleted_count = 0
        for session in sessions_to_delete:
            result = sessions.delete_one({"_id": session["_id"]})
            if result.deleted_count > 0:
                deleted_count += 1
        
        return {
            "message": f"Cleanup completed successfully",
            "sessions_kept": len(sessions_to_keep),
            "sessions_deleted": deleted_count,
            "total_before": len(all_sessions),
            "total_after": len(sessions_to_keep)
        }
        
    except Exception as e:
        return {"error": f"Failed to cleanup sessions: {str(e)}"}


