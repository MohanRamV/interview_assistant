#  AI Interview Agent

A full-stack web application that simulates personalized AI interviews tailored to a candidate's resume and job description. The system analyzes documents, generates adaptive questions, scores answers, and provides real-time coaching feedback — all in an interactive chat/voice experience.
Demo Link- https://drive.google.com/file/d/1XE8CLWCN5i3moptVqfNbdsGmn9HpVyEz/view?usp=sharing

---

##  Features

- Upload resume & job description (PDF)
- Role-specific, adaptive question generation
- Real-time scoring, feedback, and tone analysis
- Interactive chat/voice-based interview flow
- Post-interview report: scores, strengths, gaps
- Secure session tracking with user authentication

---

##  Tech Stack

**Frontend**: React.js, Web Speech API, CSS-in-JS  
**Backend**: FastAPI (Python), MongoDB  
**AI Model**: Groq (LLaMA 3)  
**Parsing**: PyMuPDF + LLMs  
**Authentication**: bcrypt

---

## 📦 API Highlights

- `POST /interview/start` – Start new interview session  
- `POST /interview/next` – Answer & get next question  
- `POST /upload/resume-jd` – Upload documents  
- `GET /interview/summary/{session_id}` – View results  
- `POST /interview/security-metrics` – Log behavior  
- `POST /evaluate/interview/{session_id}` – Validate session quality

---

##  Sample Output

- Dynamic interview transcript with scores
- Adaptive follow-up questions
- Average score breakdown (clarity, relevance, technical depth, tone)
- Final recommendation (e.g., "Strong candidate")

---

##  Getting Started

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
npm start

