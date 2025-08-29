from fastapi import FastAPI
from pydantic import BaseModel, Field
from ..frontend.engine import SymptomEngine
from typing import List, Optional, Dict, Any
from ..frontend.engine import SymptomEngine   # <-- fixed: relative import

# Create FastAPI app
app = FastAPI(
    title="AI Health Assistant (Symptom Checker)",
    description="⚠️ Demo only: Not for medical use. Always consult a doctor.",
    version="0.1.0",
)

# Load the symptom engine
engine = SymptomEngine()

# Request model
class AssessmentRequest(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: Optional[str] = Field(None, description="male/female/other")
    symptoms: List[str] = Field(..., description="List of symptom strings")
    duration_days: Optional[int] = Field(None, ge=0, description="Duration of symptoms (days)")
    notes: Optional[str] = Field(None, description="Extra info")

# Response model
class AssessmentResponse(BaseModel):
    triage_level: str
    triage_reason: List[str]
    likely_conditions: List[Dict[str, Any]]
    advice: List[str]

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

# Main endpoint
@app.post("/api/assess", response_model=AssessmentResponse)
def assess(req: AssessmentRequest):
    result = engine.assess(
        age=req.age,
        sex=req.sex,
        symptoms=req.symptoms,
        duration_days=req.duration_days,
        notes=req.notes or ""
    )
    return result
