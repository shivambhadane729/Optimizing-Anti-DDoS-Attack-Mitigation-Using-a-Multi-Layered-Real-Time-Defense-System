import os
import psutil
import requests
import itertools
import httpx
from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ─────────────────────────────────────────────
# FastAPI App Setup
# ─────────────────────────────────────────────

app = FastAPI(
    title="Anti-DDoS Load Balancer",
    version="1.0.0",
    description="Load balancer for routing and monitoring backend servers"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# ─────────────────────────────────────────────
# Server Configuration
# ─────────────────────────────────────────────

# Backend servers as comma-separated URLs from env
backend_servers = os.getenv("BACKEND_SERVERS", "http://localhost:5000").split(",")

# Round-robin iterator
server_pool = itertools.cycle(backend_servers)

# ─────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────

def get_local_health(name: str = "Load Balancer") -> dict:
    """Return CPU and RAM usage of the current load balancer."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    status = 100 - max(cpu, ram)
    return {
        "name": name,
        "status": status,
        "cpu": cpu,
        "ram": ram
    }

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@router.get("/server-health", tags=["Health"])
def server_health():
    """Return health of the load balancer itself."""
    return get_local_health()

@router.get("/all-server-health", tags=["Health"])
def all_server_health():
    """
    Poll all backend servers for health stats + include self.
    """
    results = []
    for server in backend_servers:
        try:
            print(f"🌐 Fetching health from {server}")
            response = requests.get(f"{server}/server-health", timeout=2)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Received: {data}")
            results.append(data)
        except Exception as e:
            print(f"⚠️ Failed to fetch {server}: {e}")
            results.append({
                "name": server.split("//")[-1],
                "status": 0,
                "cpu": 0,
                "ram": 0
            })

    lb_health = get_local_health()
    print(f"🧠 Load Balancer health: {lb_health}")
    results.append(lb_health)

    return JSONResponse(content=results)

@router.post("/forward", tags=["Routing"])
async def forward(request: Request, path: str = "data"):
    """
    Forward request to next backend server using round-robin.
    """
    backend_url = next(server_pool)
    full_url = f"{backend_url}/{path}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=full_url,
                headers=request.headers.raw,
                content=await request.body()
            )
        return {
            "from_backend": backend_url,
            "status_code": response.status_code,
            "response": response.json()
        }
    except Exception as e:
        return {
            "error": "Server unreachable",
            "details": str(e),
            "attempted_url": full_url
        }

# ─────────────────────────────────────────────
# Mount Router
# ─────────────────────────────────────────────

app.include_router(router)
