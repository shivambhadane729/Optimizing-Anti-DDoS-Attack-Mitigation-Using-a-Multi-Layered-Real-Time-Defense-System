from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import httpx
from ..utils.load_balancer import LoadBalancer
import logging
from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/loadbalancer", tags=["Load Balancer"])

# Initialize LoadBalancer instance
load_balancer = LoadBalancer(
    health_check_interval=30,
    health_check_timeout=5,
    max_failures=3
)

# Pydantic models for validating server URLs
class ServerAdd(BaseModel):
    url: HttpUrl

class ServerRemove(BaseModel):
    url: HttpUrl

@router.on_event("startup")
async def startup_event():
    """Start background health checks."""
    await load_balancer.start()
    logger.info("✅ Load balancer health checker started")

@router.on_event("shutdown")
async def shutdown_event():
    """Stop background health checks."""
    await load_balancer.stop()
    logger.info("⛔ Load balancer health checker stopped")

@router.get("/health")
async def health_check():
    """Return the load balancer's own health metrics."""
    return load_balancer.get_health()

@router.get("/stats")
async def get_stats():
    """Return statistics for all registered servers."""
    return load_balancer.get_server_stats()

@router.post("/servers")
async def add_server(server: ServerAdd):
    """Add a new backend server to the pool."""
    success = load_balancer.add_server(str(server.url))
    if success:
        return {"message": f"✅ Server {server.url} added successfully"}
    raise HTTPException(status_code=400, detail="❌ Server already exists or invalid")

@router.delete("/servers")
async def remove_server(server: ServerRemove):
    """Remove a server from the pool."""
    success = load_balancer.remove_server(str(server.url))
    if success:
        return {"message": f"🗑️ Server {server.url} removed successfully"}
    raise HTTPException(status_code=404, detail="❌ Server not found")

@router.get("/servers")
async def list_servers():
    """List all backend servers and their health states."""
    return {
        "servers": [
            {
                "url": url,
                "status": data["status"],
                "failures": data["failures"],
                "last_check": data["last_check"],
                "stats": data["stats"]
            }
            for url, data in load_balancer.servers.items()
        ]
    }

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def forward_request(request: Request, path: str):
    """
    Forwards any incoming request to the next healthy server in the pool.
    """
    try:
        body = await request.body()
        headers = dict(request.headers)

        dummy_url = f"http://dummy/{path}"  # Placeholder; real target added in load balancer

        forwarded_req = httpx.Request(
            method=request.method,
            url=dummy_url,
            headers=headers,
            content=body
        )

        response, error = await load_balancer.forward_request(forwarded_req, path)

        if error or not response:
            raise HTTPException(status_code=503, detail=error or "No healthy servers available")

        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        logger.exception("Exception during forwarding request")
        raise HTTPException(status_code=500, detail="Internal forwarding error")
