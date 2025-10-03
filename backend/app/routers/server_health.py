from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, crud
from ..database import get_db
import logging

# ✅ Use only /server-health here (NOT /api/server-health)
router = APIRouter(
    prefix="/server-health",
    tags=["server-health"]
)

logger = logging.getLogger(__name__)


@router.get("/live/all")
async def get_all_live_server_health(request: Request, db: Session = Depends(get_db)):
    result = []
    try:
        load_balancer = getattr(request.app.state, "load_balancer", None)
        if not load_balancer:
            logger.warning("⚠️ LoadBalancer not found in app.state")
            raise HTTPException(status_code=503, detail="LoadBalancer not initialized")

        logger.info(f"✅ LoadBalancer servers: {load_balancer.servers}")

        for url, data in load_balancer.servers.items():
            result.append({
                "name": url,
                "cpu": data.get("stats", {}).get("cpu", 0),
                "ram": data.get("stats", {}).get("ram", 0),
                "status": data.get("status", "unknown")
            })

        return result

    except Exception as e:
        logger.exception("🔥 Exception in /live/all:")
        raise HTTPException(status_code=500, detail="Internal Server Error from /live/all")


    # 🔁 Fallback to database
    try:
        records = db.query(models.ServerHealth).all()
        for record in records:
            result.append({
                "name": f"Server {record.server_id}",
                "cpu": record.cpu_usage,
                "ram": record.memory_usage,
                "status": record.status
            })
        return result

    except Exception as e:
        logger.exception("💥 Error querying database for server health: %s", e)
        raise HTTPException(status_code=500, detail="Unable to fetch server health data")


@router.get("/{server_id}", response_model=List[schemas.ServerHealth])
def get_server_health(
    server_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get historical server health records for a specific server.
    """
    try:
        return crud.get_server_health(db, server_id=server_id, skip=skip, limit=limit)
    except Exception as e:
        logger.exception("💥 Failed to retrieve server health records: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve server health records")


@router.post("/{server_id}", response_model=schemas.ServerHealth)
def create_server_health(
    server_id: int,
    health: schemas.ServerHealthCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new server health entry for a specific server.
    """
    try:
        return crud.create_server_health(db=db, health=health, server_id=server_id)
    except Exception as e:
        logger.exception("💥 Failed to create server health record: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create server health record")
