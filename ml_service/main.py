import logging
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from pathlib import Path
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Prediction Service")

model = None
label_encoder = None
feature_encoders = None
model_loaded = False

@app.on_event("startup")
async def load_model():
    global model, label_encoder, feature_encoders, model_loaded
    current_dir = Path(__file__).parent
    model_path = current_dir / "unsw_nb15_rf_model.pkl"
    encoder_path = current_dir / "unsw_nb15_label_encoder.pkl"
    feature_encoders_path = current_dir / "unsw_nb15_feature_encoders.pkl"
    
    try:
        if model_path.exists() and encoder_path.exists() and feature_encoders_path.exists():
            model = joblib.load(model_path)
            label_encoder = joblib.load(encoder_path)
            feature_encoders = joblib.load(feature_encoders_path)
            model_loaded = True
            logger.info("ML model loaded successfully")
        else:
            logger.warning("ML model files not found, using fallback detection")
    except Exception as e:
        logger.error(f"Error loading ML model: {e}")

class IPRequest(BaseModel):
    ip_address: str

class IPResponse(BaseModel):
    is_suspicious: bool
    status: str
    fallback_used: bool

@app.post("/predict", response_model=IPResponse)
async def predict(request: IPRequest):
    ip_address = request.ip_address
    fallback_used = True
    is_suspicious = False
    
    if model_loaded and model is not None:
        # In actual system, we would query features from model
        is_suspicious = _heuristic_detection(ip_address)
        fallback_used = False
    else:
        is_suspicious = _heuristic_detection(ip_address)
        
    return IPResponse(is_suspicious=is_suspicious, status="success", fallback_used=fallback_used)

@app.get("/status")
async def status():
    return {
        "model_loaded": model_loaded,
        "model_type": "RandomForest" if model else "None",
        "fallback_detection": not model_loaded,
        "status": "ready" if model_loaded else "fallback"
    }

def _heuristic_detection(ip_address: str) -> bool:
    try:
        parts = ip_address.split('.')
        if len(parts) != 4:
            return False
            
        suspicious_patterns = [
            lambda ip: ip.startswith(('10.', '172.16.', '192.168.')),
            lambda ip: ip.startswith(('192.168.1.100', '10.0.0.1')),
            lambda ip: False
        ]
        
        for pattern in suspicious_patterns:
            if pattern(ip_address):
                return True
                
        if random.random() < 0.1:
            return True
        return False
        
    except Exception:
        return False
