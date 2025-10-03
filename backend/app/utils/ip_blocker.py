import subprocess
import logging
import platform
from typing import List, Dict, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.blocked_ip import BlockedIP
from ..schemas import SecurityEventCreate
from ..crud import create_security_event

logger = logging.getLogger(__name__)

def _run_windows_firewall_command(command: List[str]) -> subprocess.CompletedProcess:
    """Run a Windows Firewall command."""
    try:
        # Use netsh advfirewall for Windows Firewall management
        result = subprocess.run(
            ["netsh", "advfirewall", "firewall"] + command,
            capture_output=True,
            text=True,
            check=False,
            shell=True
        )
        if result.returncode != 0:
            logger.error(f"Windows Firewall command failed: {result.stderr}")
        return result
    except Exception as e:
        logger.error(f"Error running Windows Firewall command: {e}")
        raise

def _run_linux_iptables_command(command: List[str]) -> subprocess.CompletedProcess:
    """Run an iptables command on Linux."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(f"iptables command failed: {result.stderr}")
        return result
    except Exception as e:
        logger.error(f"Error running iptables command: {e}")
        raise

def block_ip(ip: str, db: Session, reason: str = "Suspicious activity") -> bool:
    """Block an IP address using the appropriate firewall for the platform."""
    from . import crud
    
    # Check if IP is already blocked
    if get_blocked_ips(db, ip=ip):
        logger.info(f"IP {ip} is already blocked")
        return True

    try:
        if platform.system() == "Windows":
            # Windows Firewall blocking
            rule_name = f"BlockIP_{ip.replace('.', '_')}"
            result = _run_windows_firewall_command([
                "add", "rule", 
                f"name={rule_name}",
                "dir=in", 
                "action=block", 
                f"remoteip={ip}"
            ])
        else:
            # Linux iptables blocking
            result = _run_linux_iptables_command(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])

        if result.returncode == 0:
            # Log the blocked IP in the database
            blocked_ip = BlockedIP(ip_address=ip, reason=reason, blocked_at=datetime.now(timezone.utc))
            db.add(blocked_ip)
            
            # Create security event
            event = SecurityEventCreate(
                event_type="IP_BLOCK",
                source_ip=ip,
                severity="high",
                description=f"IP {ip} blocked: {reason}",
                status="resolved",
                details={"action": "blocked", "reason": reason, "platform": platform.system()}
            )
            create_security_event(db, event)
            db.commit()
            
            logger.info(f"Successfully blocked IP {ip} using {platform.system()} firewall")
            return True
        else:
            logger.error(f"Failed to block IP {ip}: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error blocking IP {ip}: {e}")
        return False

def unblock_ip(ip: str, db: Session) -> bool:
    """Unblock an IP address using the appropriate firewall for the platform."""
    from . import crud
    
    try:
        if platform.system() == "Windows":
            # Windows Firewall unblocking
            rule_name = f"BlockIP_{ip.replace('.', '_')}"
            result = _run_windows_firewall_command([
                "delete", "rule", 
                f"name={rule_name}"
            ])
        else:
            # Linux iptables unblocking
            result = _run_linux_iptables_command(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])

        if result.returncode == 0:
            # Update the blocked IP record in the database
            blocked_ip = db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
            if blocked_ip:
                blocked_ip.unblocked_at = datetime.now(timezone.utc)
                blocked_ip.is_active = False
                
                # Create security event
                event = SecurityEventCreate(
                    event_type="IP_UNBLOCK",
                    source_ip=ip,
                    severity="low",
                    description=f"IP {ip} unblocked",
                    status="resolved",
                    details={"action": "unblocked", "platform": platform.system()}
                )
                create_security_event(db, event)
                db.commit()
                
            logger.info(f"Successfully unblocked IP {ip}")
            return True
        else:
            logger.error(f"Failed to unblock IP {ip}: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error unblocking IP {ip}: {e}")
        return False

def get_blocked_ips(db: Session, ip: Optional[str] = None) -> List[Dict]:
    """Get list of blocked IPs from the database."""
    try:
        query = db.query(BlockedIP).filter(BlockedIP.is_active == True)
        if ip:
            query = query.filter(BlockedIP.ip_address == ip)
        return [
            {
                "ip_address": blocked_ip.ip_address,
                "reason": blocked_ip.reason,
                "blocked_at": blocked_ip.blocked_at,
                "unblocked_at": blocked_ip.unblocked_at,
                "is_active": blocked_ip.is_active
            }
            for blocked_ip in query.all()
        ]
    except Exception as e:
        logger.error(f"Error getting blocked IPs: {e}")
        return []
