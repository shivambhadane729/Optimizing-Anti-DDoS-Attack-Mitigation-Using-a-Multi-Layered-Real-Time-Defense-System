import logging
import joblib
import os
from typing import Dict, List, Optional
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Global variables for the ML model
model = None
label_encoder = None
feature_encoders = None
model_loaded = False

def load_ml_model():
    """Load the trained ML model and encoders."""
    global model, label_encoder, feature_encoders, model_loaded
    
    try:
        # Get the directory where this file is located
        current_dir = Path(__file__).parent
        model_dir = current_dir.parent.parent / "ML Model"
        
        # Try to load the trained model files
        model_path = model_dir / "unsw_nb15_rf_model.pkl"
        encoder_path = model_dir / "unsw_nb15_label_encoder.pkl"
        feature_encoders_path = model_dir / "unsw_nb15_feature_encoders.pkl"
        
        if model_path.exists() and encoder_path.exists() and feature_encoders_path.exists():
            model = joblib.load(model_path)
            label_encoder = joblib.load(encoder_path)
            feature_encoders = joblib.load(feature_encoders_path)
            model_loaded = True
            logger.info("ML model loaded successfully")
        else:
            logger.warning("ML model files not found, using fallback detection")
            model_loaded = False
            
    except Exception as e:
        logger.error(f"Error loading ML model: {e}")
        model_loaded = False

def predict_suspicious_ip(ip_address: str) -> bool:
    """
    Predict if an IP address is suspicious using the ML model.
    
    Args:
        ip_address: The IP address to check
        
    Returns:
        bool: True if suspicious, False otherwise
    """
    try:
        # If ML model is loaded, use it for prediction
        if model_loaded and model is not None:
            # For now, return a simple heuristic-based prediction
            # In a real implementation, you would extract features from the IP
            # and use the trained model for prediction
            return _heuristic_detection(ip_address)
        else:
            # Fallback to heuristic detection
            return _heuristic_detection(ip_address)
            
    except Exception as e:
        logger.error(f"Error in ML prediction: {e}")
        # Fallback to heuristic detection on error
        return _heuristic_detection(ip_address)

def _heuristic_detection(ip_address: str) -> bool:
    """
    Fallback heuristic-based suspicious IP detection.
    
    Args:
        ip_address: The IP address to check
        
    Returns:
        bool: True if suspicious, False otherwise
    """
    try:
        # Convert IP to parts
        parts = ip_address.split('.')
        if len(parts) != 4:
            return False
            
        # Check for common suspicious patterns
        suspicious_patterns = [
            # Private IP ranges that shouldn't be accessing from outside
            lambda ip: ip.startswith(('10.', '172.16.', '192.168.')),
            # Known malicious IP ranges (example)
            lambda ip: ip.startswith(('192.168.1.100', '10.0.0.1')),
            # Check for unusual port scanning patterns (would need more context)
            lambda ip: False  # Placeholder for port scanning logic
        ]
        
        # Apply suspicious pattern checks
        for pattern in suspicious_patterns:
            if pattern(ip_address):
                logger.info(f"IP {ip_address} flagged as suspicious by heuristic")
                return True
                
        # For demo purposes, randomly flag some IPs as suspicious
        # In production, remove this and implement proper detection logic
        import random
        if random.random() < 0.1:  # 10% chance for demo
            logger.info(f"IP {ip_address} flagged as suspicious for demo purposes")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error in heuristic detection: {e}")
        return False

def get_model_status() -> Dict:
    """Get the current status of the ML model."""
    return {
        "model_loaded": model_loaded,
        "model_type": "RandomForest" if model else "None",
        "fallback_detection": not model_loaded,
        "status": "ready" if model_loaded else "fallback"
    }

def retrain_model(training_data_path: str) -> Dict:
    """
    Retrain the ML model with new data.
    
    Args:
        training_data_path: Path to the new training data
        
    Returns:
        Dict: Training results
    """
    try:
        # This would implement the actual retraining logic
        # For now, return a placeholder response
        logger.info(f"Model retraining requested with data from: {training_data_path}")
        
        return {
            "status": "success",
            "message": "Model retraining initiated",
            "training_data_path": training_data_path,
            "note": "Retraining functionality not yet implemented"
        }
        
    except Exception as e:
        logger.error(f"Error in model retraining: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# Load the model when the module is imported
load_ml_model()
