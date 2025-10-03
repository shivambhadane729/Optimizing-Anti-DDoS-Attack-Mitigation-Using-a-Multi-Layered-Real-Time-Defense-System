from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.models.attack_log import AttackLog
from app.database import get_db, init_db
from app.routers import dashboard, load_balancer, server_health
from app.utils.load_balancer import LoadBalancer
from dotenv import load_dotenv
from typing import List
from concurrent.futures import ThreadPoolExecutor
import logging
import asyncio
import time
import uvicorn
import psutil
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global tracking variables
connected_clients: List[WebSocket] = []
traffic_stats = {
    "clean_requests": 0,
    "malicious_requests": 0,
    "last_update": time.time()
}
db_executor = ThreadPoolExecutor(max_workers=20)
request_counts = {}

# Lifespan event for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.load_balancer = LoadBalancer()
    await app.state.load_balancer.start()

    # Inject dummy servers
    app.state.load_balancer.servers["http://localhost:8001"] = {
        "stats": {"cpu": 42.5, "ram": 68.2},
        "status": "healthy"
    }
    app.state.load_balancer.servers["http://localhost:8002"] = {
        "stats": {"cpu": 37.0, "ram": 55.1},
        "status": "healthy"
    }

    logger.info("✅ Lifespan startup complete")
    logger.info(f"🔁 LoadBalancer started with servers: {app.state.load_balancer.servers}")

    yield

    await app.state.load_balancer.stop()
    logger.info("🛑 Lifespan shutdown complete")


# FastAPI app instance
app = FastAPI(
    title="Anti-DDOS System API",
    description="Backend API for the Anti-DDOS System Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiting middleware
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"]
)

# Include API routers
app.include_router(server_health.router)
app.include_router(dashboard.router)
app.include_router(load_balancer.router)

# WebSocket route for real-time server updates
@app.websocket("/ws/server-health")
async def websocket_server_health(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({"message": "🟢 Server live update"})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.warning("WebSocket disconnected")

# API endpoint for recent attack logs
@app.get("/api/dashboard/attack-logs")
async def get_attack_logs(db: Session = Depends(get_db)):
    return db.query(AttackLog).order_by(AttackLog.timestamp.desc()).limit(100).all()

# Uvicorn entry point for development
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        timeout_keep_alive=30,
        limit_concurrency=100,
        backlog=128,
        loop="uvloop",
        http="httptools",
        log_level="info"
    )
@app.get("/server-health")
def server_health():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    return JSONResponse({
        "name": "localhost:5000",
        "status": "healthy",
        "cpu": cpu,
        "ram": ram
    })
