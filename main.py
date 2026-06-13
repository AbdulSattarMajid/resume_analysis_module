import os
import shutil
import base64 # 🌟 NEW: Needed to encode the PDF for React
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import your existing engine logic
from engine.parser import extract_content
from engine.analyzer import analyze_skills
from engine.grammar import check_grammar
from engine.experience import calculate_experience
from engine.reporter import generate_pdf_report # 🌟 Ensure this is active

app = FastAPI(title="PrepMate API", description="ATS Resume Analysis Engine")

# --- 1. CORS CONFIGURATION ---
# This allows your partner's React frontend to talk to this Python backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with the specific React URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. THE ANALYSIS ENDPOINT ---
@app.post("/analyze")
async def analyze_application(
    role: str = Form(...),
    jd_text: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Entry point for React:
    Receives File, Role, and JD. 
    Returns JSON results + Base64 PDF.
    """
    # Create a temporary file to process the upload
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # PHASE 1: Extraction & Logic
        raw_text = extract_content(temp_path)
        
        # Skill matching
        skill_results = analyze_skills(raw_text, jd_text, role)
        jd_score = skill_results['score']
        
        # Grammar and Experience
        grammar_errors = check_grammar(raw_text)
        years_exp = calculate_experience(raw_text)

        # 🌟 NEW: Generate the PDF and encode it to Base64
        pdf_bytes = generate_pdf_report(skill_results, role, grammar_errors, jd_score)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # PHASE 2: Return JSON Response
        return {
            "status": "success",
            "results": {
                "score": jd_score,
                "years_of_experience": years_exp,
                "grammar_issue_count": len(grammar_errors),
                "grammar_details": grammar_errors,
                "skills_breakdown": skill_results['detailed'],
                "total_found": skill_results['found'],
                "total_missing": skill_results['missing'],
                "pdf_report": pdf_base64 # 🌟 NEW: Send PDF to React
            }
        }

    except Exception as e:
        # If something breaks, tell the frontend exactly what happened
        raise HTTPException(status_code=500, detail=f"Analysis Error: {str(e)}")

    finally:
        # Cleanup: Remove the temp file after processing
        if os.path.exists(temp_path):
            os.remove(temp_path)

# --- 3. RUN THE SERVER ---
if __name__ == "__main__":
    import uvicorn
    # This starts the server on http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)