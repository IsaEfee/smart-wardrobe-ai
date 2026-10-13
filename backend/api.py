import os
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .database import (
    init_db,
    create_or_update_user,
    get_user,
    get_or_create_default_user,
    save_user_wardrobe,
    get_user_wardrobe,
    record_user_feedback,
    get_user_feedback_history
)
from .engine import load_db, generate_recommendations, get_current_weather

app = FastAPI(
    title="Smart AI Wardrobe Assistant API",
    description="Adaptive Human-in-the-Loop Hybrid ML & Thermodynamics Recommender Engine",
    version="2.0.0"
)

# Enable CORS so mobile apps (React Native / Flutter) or web frontends can call it freely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

# --- Pydantic Schemas ---
class UserProfileSchema(BaseModel):
    user_id: Optional[int] = None
    name: str = "İsa"
    gender: str = Field(default="Male", description="Male or Female")
    base_thermal_profile: str = Field(default="Standard", description="Cold, Standard, or Hot")
    has_umbrella: bool = True
    has_undershirt: bool = True

class WardrobeSaveSchema(BaseModel):
    top_inner: List[str] = []
    top_outer: List[str] = []
    bottom_inner: List[str] = []
    bottom_outer: List[str] = []
    accessories: List[str] = []

class RecommendRequestSchema(BaseModel):
    user_id: Optional[int] = None
    city: str = "Istanbul"
    start_offset: int = 0
    duration: int = 4
    lang: str = "tr"

class FeedbackRequestSchema(BaseModel):
    user_id: int
    feedback: str = Field(..., description="'cold' (üşüdüm), 'perfect' (ideal), or 'hot' (terledim)")
    temp_c: float = 20.0
    base_clo: float = 0.8

# --- Endpoints ---

@app.get("/")
def root():
    return {
        "status": "online",
        "name": "Smart Wardrobe Assistant API",
        "version": "2.0.0",
        "documentation": "/docs"
    }

@app.get("/api/clothes")
def get_all_clothes():
    """Returns the full wardrobe catalog grouped by category."""
    return load_db()

@app.post("/api/user")
def save_user(profile: UserProfileSchema):
    """Creates or updates user profile."""
    uid = create_or_update_user(
        user_id=profile.user_id,
        name=profile.name,
        gender=profile.gender,
        base_thermal=profile.base_thermal_profile,
        has_umbrella=profile.has_umbrella,
        has_undershirt=profile.has_undershirt
    )
    return {"success": True, "user_id": uid, "message": "User profile saved successfully."}

@app.get("/api/user/{user_id}")
def fetch_user_profile(user_id: int):
    """Fetches user profile, current learning delta, and owned wardrobe items."""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    wardrobe = get_user_wardrobe(user_id)
    return {
        "user": user,
        "wardrobe": wardrobe
    }

@app.get("/api/user/default/profile")
def fetch_default_profile():
    """Convenience endpoint returning the default user (creating if none exists)."""
    user = get_or_create_default_user()
    wardrobe = get_user_wardrobe(user["id"])
    
    # If wardrobe is empty, populate with all basic items by default
    if not any(wardrobe.values()):
        db = load_db()
        init_items = {
            "top_inner": [x["en"] for x in db["top_inner"] if user["gender"] in x["gender"]],
            "top_outer": [x["en"] for x in db["top_outer"] if user["gender"] in x["gender"]],
            "bottom_inner": [x["en"] for x in db["bottom_inner"] if user["gender"] in x["gender"]],
            "bottom_outer": [x["en"] for x in db["bottom_outer"] if user["gender"] in x["gender"]],
            "accessories": [x["en"] for x in db["accessories"]]
        }
        save_user_wardrobe(user["id"], init_items)
        wardrobe = init_items
        
    return {
        "user": user,
        "wardrobe": wardrobe
    }

@app.post("/api/user/{user_id}/wardrobe")
def update_user_wardrobe(user_id: int, wardrobe: WardrobeSaveSchema):
    """Updates user's persistent wardrobe."""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    save_user_wardrobe(user_id, wardrobe.dict())
    return {"success": True, "message": "Wardrobe saved successfully."}

@app.post("/api/recommend")
def get_recommendation(req: RecommendRequestSchema):
    """
    Main endpoint for mobile/web apps.
    Fetches user profile, owned wardrobe, applies dynamic personalization delta, and returns 3 diverse outfits.
    """
    if req.user_id:
        user = get_user(req.user_id)
    else:
        user = get_or_create_default_user()
        
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    wardrobe = get_user_wardrobe(user["id"])
    if not any(wardrobe.values()):
        # Auto-seed wardrobe if empty
        db = load_db()
        wardrobe = {
            "top_inner": [x["en"] for x in db["top_inner"] if user["gender"] in x["gender"]],
            "top_outer": [x["en"] for x in db["top_outer"] if user["gender"] in x["gender"]],
            "bottom_inner": [x["en"] for x in db["bottom_inner"] if user["gender"] in x["gender"]],
            "bottom_outer": [x["en"] for x in db["bottom_outer"] if user["gender"] in x["gender"]],
            "accessories": [x["en"] for x in db["accessories"]]
        }
        save_user_wardrobe(user["id"], wardrobe)

    res = generate_recommendations(
        user_gender=user["gender"],
        base_thermal_profile=user["base_thermal_profile"],
        personal_delta_clo=user["personal_delta_clo"],
        has_umbrella=bool(user["has_umbrella"]),
        has_undershirt=bool(user["has_undershirt"]),
        user_wardrobe_items=wardrobe,
        city=req.city,
        start_offset=req.start_offset,
        duration=req.duration,
        lang=req.lang
    )
    return res

@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequestSchema):
    """
    Human-in-the-Loop Online Learning Endpoint:
    Receives daily user feedback ('cold', 'perfect', 'hot') and mathematically adjusts personal_delta_clo.
    """
    user = get_user(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    result = record_user_feedback(
        user_id=req.user_id,
        feedback=req.feedback,
        temp_c=req.temp_c,
        base_clo=req.base_clo
    )
    return {
        "success": True,
        "learning_result": result
    }

@app.get("/api/feedback/history/{user_id}")
def fetch_learning_history(user_id: int):
    """Returns history of user feedback and the convergence of their personal delta CLO."""
    history = get_user_feedback_history(user_id)
    return {"user_id": user_id, "history": history}
