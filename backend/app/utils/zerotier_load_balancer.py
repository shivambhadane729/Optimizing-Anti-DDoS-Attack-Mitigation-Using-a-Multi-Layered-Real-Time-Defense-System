import asyncio
import logging
import time
from typing import Dict, Optional, Tuple
import httpx
import itertools
from app.utils.ml_model import predict_suspicious_ip  # your ML model

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DemoLoadBalancer:
    def __init__(self, health_check_interval: int = 10, max_failures: int = 3):
        self.health_check_interval = health_check_interval
        self.max_failures = max_failures
        self.servers: Dict[str, Dict] = {}
        self.current_index = 0
        self._health_check_task = None

        # Demo backend servers (localhost)
        self.backend_servers = ["127.0.0.1:8001", "127.0.0.1:8002"]
        for ip in self.backend_servers:
            self.servers[ip] = {"status": "healthy", "failures": 0, "last_check": time.time()}

    async def start(self):
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Demo load balancer started")

    async def stop(self):
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Demo load balancer stopped")

    async def _health_check_loop(self):
        """Periodically check backend health."""
        while True:
            async with httpx.AsyncClient(timeout=2.0) as client:
                for ip in list(self.servers.keys()):
                    try:
                        response = await client.get(f"http://{ip}/health")
                        if response.status_code == 200:
                            self.servers[ip]["status"] = "healthy"
                            self.servers[ip]["failures"] = 0
                        else:
                            self._handle_server_failure(ip)
                    except Exception as e:
                        logger.warning(f"Health check failed for {ip}: {e}")
                        self._handle_server_failure(ip)
                    self.servers[ip]["last_check"] = time.time()
            await asyncio.sleep(self.health_check_interval)

    def _handle_server_failure(self, ip: str):
        self.servers[ip]["failures"] += 1
        if self.servers[ip]["failures"] >= self.max_failures:
            self.servers[ip]["status"] = "unhealthy"
            logger.warning(f"Server {ip} marked unhealthy after {self.max_failures} failures")

    def get_next_server(self) -> Optional[str]:
        healthy_servers = [ip for ip, data in self.servers.items() if data["status"] == "healthy"]
        if not healthy_servers:
            return None
        server = healthy_servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(healthy_servers)
        return server

    async def forward_request(self, request: httpx.Request, path: str, client_ip: str) -> Tuple[Optional[httpx.Response], Optional[str]]:
        """Forward a request to next healthy server with ML blocking."""
        # ML-based IP blocking
        if predict_suspicious_ip(client_ip):
            logger.warning(f"Blocked request from suspicious IP: {client_ip}")
            return httpx.Response(status_code=403, content=b"Blocked by ML model"), None

        server = self.get_next_server()
        if not server:
            return httpx.Response(status_code=503, content=b"No healthy servers available"), None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"http://{server}/{path}"
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers=dict(request.headers),
                    content=await request.body()
                )
                return response, None
        except Exception as e:
            logger.error(f"Error forwarding request to {server}: {e}")
            self._handle_server_failure(server)
            return None, str(e)

    def get_server_stats(self) -> Dict:
        return {
            "total_servers": len(self.servers),
            "healthy_servers": len([s for s in self.servers.values() if s["status"] == "healthy"]),
            "unhealthy_servers": len([s for s in self.servers.values() if s["status"] == "unhealthy"]),
            "servers": {
                ip: {
                    "status": data["status"],
                    "failures": data["failures"],
                    "last_check": data["last_check"]
                } for ip, data in self.servers.items()
            }
        }

# -----------------------------
# Demo usage with FastAPI
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI, Request

    app = FastAPI()
    lb = DemoLoadBalancer()

    @app.on_event("startup")
    async def startup_event():
        await lb.start()

    @app.on_event("shutdown")
    async def shutdown_event():
        await lb.stop()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def proxy(request: Request, path: str):
        client_ip = request.client.host
        resp, err = await lb.forward_request(request, path, client_ip)
        if resp:
            return resp
        return {"error": err}

    uvicorn.run(app, host="0.0.0.0", port=5000)

# -----------------------------
# ZeroTier Load Balancer Class
# -----------------------------
class ZeroTierLoadBalancer:
    def __init__(self, zerotier_manager, health_check_interval: int = 30, health_check_timeout: int = 5, max_failures: int = 3):
        self.zerotier_manager = zerotier_manager
        self.health_check_interval = health_check_interval
        self.health_check_timeout = health_check_timeout
        self.max_failures = max_failures
        self.servers: Dict[str, Dict] = {}
        self.current_index = 0
        self._health_check_task = None
        
        # Initialize with ZeroTier network members
        self._load_zerotier_servers()
        
    def _load_zerotier_servers(self):
        """Load servers from ZeroTier network members."""
        try:
            members = self.zerotier_manager.get_network_members()
            for member in members:
                if member.get("authorized", False):
                    ip = self.zerotier_manager.get_member_ip(member["nodeId"])
                    if ip:
                        self.servers[ip] = {
                            "status": "unknown",
                            "failures": 0,
                            "last_check": 0,
                            "node_id": member["nodeId"],
                            "name": member.get("name", "Unknown"),
                            "physical_ip": member.get("physicalIp", "Unknown")
                        }
            logger.info(f"Loaded {len(self.servers)} ZeroTier servers")
        except Exception as e:
            logger.error(f"Error loading ZeroTier servers: {e}")

    def start(self):
        """Start the load balancer health checks."""
        logger.info("ZeroTier load balancer started")
        # Note: Health checks would be implemented here in a real implementation

    async def stop(self):
        """Stop the load balancer."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("ZeroTier load balancer stopped")

    def get_server_stats(self) -> Dict:
        """Get current server statistics."""
        return {
            "total_servers": len(self.servers),
            "healthy_servers": len([s for s in self.servers.values() if s["status"] == "healthy"]),
            "unhealthy_servers": len([s for s in self.servers.values() if s["status"] == "unhealthy"]),
            "servers": {
                ip: {
                    "status": data["status"],
                    "failures": data["failures"],
                    "last_check": data["last_check"],
                    "node_id": data.get("node_id"),
                    "name": data.get("name"),
                    "physical_ip": data.get("physical_ip")
                }
                for ip, data in self.servers.items()
            }
        }

    async def forward_request(self, request: httpx.Request, path: str) -> Tuple[Optional[httpx.Response], Optional[str]]:
        """Forward a request to a ZeroTier server."""
        # For now, return a simple response
        # In a real implementation, this would forward to actual ZeroTier servers
        return httpx.Response(
            status_code=200,
            content=b"Request forwarded to ZeroTier network",
            headers={"Content-Type": "text/plain"}
        ), None
