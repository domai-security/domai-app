#!/usr/bin/env python3
"""
DōmAI Permission Management System
Handles elevated privileges securely with user consent and audit logging
"""

import os
import pwd
import grp
import logging
import asyncio
from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

class PrivilegeLevel(Enum):
    NORMAL = "normal"         # No special privileges
    ELEVATED = "elevated"     # Some system access (e.g., reading system files)
    ADMIN = "admin"          # Full system access (requires sudo/root)

@dataclass
class Permission:
    name: str
    level: PrivilegeLevel
    description: str
    reason: str
    commands: List[str]
    alternatives: List[str]

class PermissionManager:
    """Manages system permissions and privileged operations"""
    
    def __init__(self):
        self.granted_permissions: Set[str] = set()
        self.audit_log = []
        self.permission_cache = {}
        
        # Define known permissions
        self.permissions: Dict[str, Permission] = {
            "packet_capture": Permission(
                name="packet_capture",
                level=PrivilegeLevel.ADMIN,
                description="Capture network packets",
                reason="Required for network monitoring and security analysis",
                commands=["tcpdump"],
                alternatives=["Wireshark (GUI)", "tshark (CLI)"]
            ),
            "process_monitor": Permission(
                name="process_monitor",
                level=PrivilegeLevel.ELEVATED,
                description="Monitor system processes",
                reason="Required for security monitoring",
                commands=["ps", "top", "lsof"],
                alternatives=["Activity Monitor (GUI)"]
            ),
            "file_monitor": Permission(
                name="file_monitor",
                level=PrivilegeLevel.ELEVATED,
                description="Monitor filesystem changes",
                reason="Required for security monitoring",
                commands=["fswatch", "fs_usage"],
                alternatives=["Folder watching (limited)"]
            )
        }
        
    async def check_permission(self, permission_name: str) -> bool:
        """Check if permission is currently granted"""
        return permission_name in self.granted_permissions
        
    async def request_permission(self, permission_name: str) -> bool:
        """Request permission from user with full context"""
        if permission_name not in self.permissions:
            logging.error(f"Unknown permission requested: {permission_name}")
            return False
            
        perm = self.permissions[permission_name]
        
        # Check if already granted
        if permission_name in self.granted_permissions:
            return True
            
        try:
            # Log permission request
            self._log_request(permission_name, perm.level)
            
            # Get current process privileges
            current_privileges = await self._get_current_privileges()
            
            # Check if we need elevation
            if perm.level == PrivilegeLevel.ADMIN and current_privileges != PrivilegeLevel.ADMIN:
                elevated = await self._request_elevation(perm)
                if not elevated:
                    return False
                    
            # Grant permission
            self.granted_permissions.add(permission_name)
            self._log_grant(permission_name)
            
            return True
            
        except Exception as e:
            logging.error(f"Permission request failed: {str(e)}")
            return False
            
    async def release_permission(self, permission_name: str):
        """Release a previously granted permission"""
        if permission_name in self.granted_permissions:
            self.granted_permissions.remove(permission_name)
            self._log_release(permission_name)
            
    async def get_command_wrapper(self, command: str) -> Optional[str]:
        """Get appropriate wrapper for privileged command"""
        # Find permission that includes this command
        for perm in self.permissions.values():
            if command in perm.commands:
                if await self.check_permission(perm.name):
                    if perm.level == PrivilegeLevel.ADMIN:
                        return "sudo"  # Use sudo for admin commands
                break
                
        return None
        
    async def _get_current_privileges(self) -> PrivilegeLevel:
        """Determine current process privileges"""
        if os.geteuid() == 0:
            return PrivilegeLevel.ADMIN
            
        # Check group membership
        groups = [g.gr_name for g in grp.getgrall() if pwd.getpwuid(os.getuid())[0] in g.gr_mem]
        if "admin" in groups:
            return PrivilegeLevel.ELEVATED
            
        return PrivilegeLevel.NORMAL
        
    async def _request_elevation(self, permission: Permission) -> bool:
        """Request privilege elevation from user"""
        # This would integrate with system's privilege elevation
        # For now, we'll assume it's handled externally
        return True
        
    def _log_request(self, permission_name: str, level: PrivilegeLevel):
        """Log permission request"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "request",
            "permission": permission_name,
            "level": level.value,
            "process_id": os.getpid(),
            "user": pwd.getpwuid(os.getuid())[0]
        }
        self.audit_log.append(entry)
        logging.info(f"Permission requested: {json.dumps(entry)}")
        
    def _log_grant(self, permission_name: str):
        """Log permission grant"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "grant",
            "permission": permission_name,
            "process_id": os.getpid(),
            "user": pwd.getpwuid(os.getuid())[0]
        }
        self.audit_log.append(entry)
        logging.info(f"Permission granted: {json.dumps(entry)}")
        
    def _log_release(self, permission_name: str):
        """Log permission release"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "release",
            "permission": permission_name,
            "process_id": os.getpid(),
            "user": pwd.getpwuid(os.getuid())[0]
        }
        self.audit_log.append(entry)
        logging.info(f"Permission released: {json.dumps(entry)}")
        
    def get_audit_log(self) -> List[Dict]:
        """Get complete audit log"""
        return self.audit_log.copy()
