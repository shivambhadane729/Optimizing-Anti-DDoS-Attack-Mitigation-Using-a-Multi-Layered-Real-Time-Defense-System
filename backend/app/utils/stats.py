import psutil
import logging
import platform
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..models.server import Server
from ..models.security_event import SecurityEvent

logger = logging.getLogger(__name__)

def get_stats(db: Session) -> Dict[str, Any]:
    """Get system statistics including CPU, memory, network, and security metrics."""
    try:
        # System stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Get disk usage for the appropriate platform
        if platform.system() == "Windows":
            # Use C: drive on Windows
            disk = psutil.disk_usage('C:\\')
        else:
            # Use root directory on Unix-like systems
            disk = psutil.disk_usage('/')
            
        net_io = psutil.net_io_counters()
        
        # Security stats
        total_events = db.query(SecurityEvent).count()
        active_events = db.query(SecurityEvent).filter(
            SecurityEvent.status == "active"
        ).count()
        
        # Get events in last 24 hours
        last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_events = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= last_24h
        ).count()
        
        # Server stats
        total_servers = db.query(Server).count()
        active_servers = db.query(Server).filter(
            Server.status == "active"
        ).count()
        
        return {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_used": disk.used,
                "disk_total": disk.total,
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
            },
            "security": {
                "total_events": total_events,
                "active_events": active_events,
                "events_last_24h": recent_events
            },
            "servers": {
                "total": total_servers,
                "active": active_servers
            },
            "timestamp": datetime.now(timezone.utc)
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }

def get_uptime() -> Dict[str, Any]:
    """Get system uptime information."""
    try:
        # Get boot time, handling potential Windows issues
        try:
            boot_time = psutil.boot_time()
            uptime = datetime.fromtimestamp(boot_time)
        except (OSError, AttributeError):
            # Fallback for Windows or other issues
            import time
            boot_time = time.time() - 3600  # Assume 1 hour ago as fallback
            uptime = datetime.fromtimestamp(boot_time)
            
        now = datetime.now()
        uptime_delta = now - uptime
        
        return {
            "boot_time": uptime,
            "uptime_seconds": uptime_delta.total_seconds(),
            "uptime_days": uptime_delta.days,
            "uptime_hours": uptime_delta.seconds // 3600,
            "uptime_minutes": (uptime_delta.seconds % 3600) // 60
        }
    except Exception as e:
        logger.error(f"Error getting uptime: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        } 