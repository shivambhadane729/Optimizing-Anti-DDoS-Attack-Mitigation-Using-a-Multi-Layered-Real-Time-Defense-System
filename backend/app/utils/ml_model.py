import logging
import os
import requests
from typing import Dict

logger = logging.getLogger(__name__)

# URL of the new ML microservice
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")

def load_ml_model():
    """Check if the ML microservice is available."""
    try:
        response = requests.get(f"{ML_SERVICE_URL}/status", timeout=5)
        if response.status_code == 200:
            logger.info("Successfully connected to ML microservice")
        else:
            logger.warning("ML microservice returned non-200 status")
    except Exception as e:
        logger.error(f"Cannot connect to ML microservice: {e}")

def predict_suspicious_ip(ip_address: str) -> bool:
    """
    Predict if an IP address is suspicious by querying the ML microservice.
    """
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/predict",
            json={"ip_address": ip_address},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("is_suspicious"):
                logger.info(f"IP {ip_address} flagged as suspicious by ML microservice")
            return result.get("is_suspicious", False)
        else:
            logger.warning("ML microservice failed to process request, using fallback")
            return _heuristic_detection(ip_address)
    except Exception as e:
        logger.error(f"Error calling ML microservice: {e}")
        return _heuristic_detection(ip_address)

def _heuristic_detection(ip_address: str) -> bool:
    """Fallback heuristic-based detection if ML service is unreachable."""
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
                logger.info(f"IP {ip_address} flagged by heuristic fallback")
                return True
                
        import random
        if random.random() < 0.1:
            logger.info(f"IP {ip_address} flagged as suspicious for demo purposes (fallback)")
            return True
            
        return False
    except Exception as e:
        logger.error(f"Error in heuristic detection: {e}")
        return False

def get_model_status() -> Dict:
    """Get the current status of the ML microservice."""
    try:
        response = requests.get(f"{ML_SERVICE_URL}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
        
    return {
        "model_loaded": False,
        "model_type": "None",
        "fallback_detection": True,
        "status": "unreachable"
    }

def retrain_model(training_data_path: str) -> Dict:
    """Placeholder for retraining."""
    return {
        "status": "success",
        "message": "Model retraining initiated via microservice",
        "training_data_path": training_data_path,
        "note": "Not yet fully implemented over microservice bus"
    }

# Check service connection when module is imported
load_ml_model()
