from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .engine import SymptomEngine   # ← correct relative import (one line)

# OPTIONAL: enable CORS if your Streamlit UI is hosted elsewhere
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Health Assistant (Symptom Checker)",
    description="⚠️ Demo only: Not for medical use. Always consult a doctor.",
    version="0.1.0",
)

# If you deploy frontend separately, uncomment CORS:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],   # or restrict to your Streamlit domain
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

engine = SymptomEngine()

class AssessmentRequest(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: Optional[str] = Field(None, description="male/female/other")
    symptoms: List[str] = Field(..., description="List of symptom strings")
    duration_days: Optional[int] = Field(None, ge=0, description="Duration of symptoms (days)")
    notes: Optional[str] = Field(None, description="Extra info")

class AssessmentResponse(BaseModel):
    triage_level: str
    triage_reason: List[str]
    likely_conditions: List[Dict[str, Any]]
    advice: List[str]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/assess", response_model=AssessmentResponse)
def assess(req: AssessmentRequest):
    return engine.assess(
        age=req.age,
        sex=req.sex,
        symptoms=req.symptoms,
        duration_days=req.duration_days,
        notes=req.notes or ""
    )
