from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
from ..database import get_db
from ..utils.ip_blocker import block_ip, unblock_ip, get_blocked_ips
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ipblock/block")
async def block_ip_route(ip: str, db: Session = Depends(get_db)):
    """Block an IP address and log it in the database."""
    if not block_ip(ip, db, "Manual block"):
        raise HTTPException(status_code=500, detail="Failed to block IP")
    
    return {
        "status": "blocked",
        "ip": ip,
        "timestamp": datetime.now(timezone.utc)
    }

@router.post("/ipblock/unblock")
async def unblock_ip_route(ip: str, db: Session = Depends(get_db)):
    """Unblock an IP address and update the database."""
    if not unblock_ip(ip, db):
        raise HTTPException(status_code=500, detail="Failed to unblock IP")
    
    return {
        "status": "unblocked",
        "ip": ip,
        "timestamp": datetime.now(timezone.utc)
    }

@router.get("/ipblock/list")
async def list_blocked_ips(db: Session = Depends(get_db)):
    """List all blocked IPs."""
    blocked_ips = get_blocked_ips(db)
    
    return [
        {
            "ip": ip["ip_address"],
            "reason": ip["reason"],
            "blocked_at": ip["blocked_at"],
            "unblocked_at": ip["unblocked_at"]
        }
        for ip in blocked_ips
    ] 