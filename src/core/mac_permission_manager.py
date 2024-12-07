#!/usr/bin/env python3
"""
DōmAI macOS Permission Manager
Handles macOS-specific permission management and security integration
"""

import os
import logging
import sqlite3
import plistlib
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json

class PermissionType(Enum):
    FULL_DISK = "full_disk"
    NETWORK = "network"
    INPUT_MONITORING = "input_monitoring"
    SCREEN_RECORDING = "screen_recording"
    ACCESSIBILITY = "accessibility"
    CAMERA = "camera"
    MICROPHONE = "microphone"

@dataclass
class MacPermission:
    type: PermissionType
    bundle_id: str
    description: str
    required_entitlements: List[str]
    tcc_service: Optional[str] = None
    command_line: Optional[str] = None

class MacPermissionManager:
    """Manages macOS permissions and security integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bundle_id = "dev.domai.security"
        self.granted_permissions: Set[PermissionType] = set()
        self.tcc_db_path = "/Library/Application Support/com.apple.TCC/TCC.db"
        self.user_tcc_db_path = os.path.expanduser("~/Library/Application Support/com.apple.TCC/TCC.db")
        
        # Define known permissions
        self.permissions: Dict[str, MacPermission] = {
            "packet_capture": MacPermission(
                type=PermissionType.NETWORK,
                bundle_id=self.bundle_id,
                description="Capture and analyze network traffic",
                required_entitlements=["com.apple.security.network.client"],
                command_line="/usr/sbin/tcpdump"
            ),
            "disk_monitor": MacPermission(
                type=PermissionType.FULL_DISK,
                bundle_id=self.bundle_id,
                description="Monitor filesystem changes",
                required_entitlements=["com.apple.security.files.all"],
                tcc_service="kTCCServiceSystemPolicyAllFiles"
            ),
            "process_monitor": MacPermission(
                type=PermissionType.ACCESSIBILITY,
                bundle_id=self.bundle_id,
                description="Monitor system processes",
                required_entitlements=["com.apple.security.automation.apple-events"],
                tcc_service="kTCCServiceAccessibility"
            )
        }
        
    async def initialize(self) -> bool:
        """Initialize permission manager and verify setup"""
        try:
            # Verify bundle existence
            if not await self._verify_bundle():
                return False
                
            # Check existing permissions
            await self._load_granted_permissions()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize permission manager: {str(e)}")
            return False
            
    async def check_permission(self, permission_name: str) -> bool:
        """Check if permission is currently granted"""
        try:
            if permission_name not in self.permissions:
                self.logger.error(f"Unknown permission: {permission_name}")
                return False
                
            perm = self.permissions[permission_name]
            
            # Check entitlements
            if not await self._verify_entitlements(perm.required_entitlements):
                return False
                
            # Check TCC permission if required
            if perm.tcc_service:
                return await self._check_tcc_permission(perm.tcc_service)
                
            # Check command line tool if specified
            if perm.command_line:
                return await self._check_command_permission(perm.command_line)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking permission {permission_name}: {str(e)}")
            return False
            
    async def request_permission(self, permission_name: str) -> bool:
        """Request permission with proper macOS dialogs"""
        try:
            if permission_name not in self.permissions:
                return False
                
            perm = self.permissions[permission_name]
            
            # Handle TCC permissions
            if perm.tcc_service:
                granted = await self._request_tcc_permission(perm.tcc_service, perm.description)
                if not granted:
                    return False
                    
            # Handle command line tools
            if perm.command_line:
                granted = await self._request_command_permission(perm.command_line)
                if not granted:
                    return False
                    
            self.granted_permissions.add(perm.type)
            await self._log_permission_grant(permission_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error requesting permission {permission_name}: {str(e)}")
            return False
            
    async def _verify_bundle(self) -> bool:
        """Verify application bundle exists and is properly signed"""
        try:
            # Check bundle existence
            bundle_path = f"/Applications/{self.bundle_id}.app"
            if not os.path.exists(bundle_path):
                self.logger.error("Application bundle not found")
                return False
                
            # Verify code signature
            result = await self._run_command(["codesign", "--verify", "--verbose", bundle_path])
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Bundle verification failed: {str(e)}")
            return False
            
    async def _verify_entitlements(self, required_entitlements: List[str]) -> bool:
        """Verify application has required entitlements"""
        try:
            # Get current entitlements
            result = await self._run_command(
                ["codesign", "--display", "--entitlements", "-", "/Applications/{self.bundle_id}.app"]
            )
            
            if result.returncode != 0:
                return False
                
            current_entitlements = plistlib.loads(result.stdout)
            
            # Check required entitlements
            for entitlement in required_entitlements:
                if entitlement not in current_entitlements:
                    self.logger.error(f"Missing required entitlement: {entitlement}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Entitlement verification failed: {str(e)}")
            return False
            
    async def _check_tcc_permission(self, service: str) -> bool:
        """Check TCC database for permission status"""
        try:
            query = """
                SELECT allowed, prompt_count
                FROM access
                WHERE service = ? AND client = ?
                ORDER BY last_modified DESC
                LIMIT 1
            """
            
            # Check system database
            sys_result = await self._query_tcc_db(self.tcc_db_path, query, (service, self.bundle_id))
            if sys_result and sys_result[0]:
                return True
                
            # Check user database
            user_result = await self._query_tcc_db(self.user_tcc_db_path, query, (service, self.bundle_id))
            return bool(user_result and user_result[0])
            
        except Exception as e:
            self.logger.error(f"Error checking TCC permission: {str(e)}")
            return False
            
    async def _request_tcc_permission(self, service: str, description: str) -> bool:
        """Request TCC permission via macOS dialog"""
        try:
            # Use AppleScript to trigger permission dialog
            script = f"""
                tell application "System Events"
                    activate
                    display dialog "{description}" ¬
                        buttons {{"Deny", "Allow"}} ¬
                        default button "Allow" ¬
                        with title "Permission Required"
                    if button returned of result is "Allow" then
                        using terms from application "System Events"
                            tell application "System Preferences"
                                activate
                                set current pane to pane "Security & Privacy"
                                delay 1
                                -- Additional steps would be needed to actually click buttons
                            end tell
                        end using terms from
                    end if
                end tell
            """
            
            result = await self._run_command(["osascript", "-e", script])
            if result.returncode != 0:
                return False
                
            # Verify permission was granted
            return await self._check_tcc_permission(service)
            
        except Exception as e:
            self.logger.error(f"Error requesting TCC permission: {str(e)}")
            return False
            
    async def _check_command_permission(self, command: str) -> bool:
        """Check if we can execute command with proper permissions"""
        try:
            result = await self._run_command([command, "--version"])
            return result.returncode == 0
        except Exception:
            return False
            
    async def _request_command_permission(self, command: str) -> bool:
        """Request permission to use command line tool"""
        try:
            # Use Security framework to request access
            script = f"""
                tell application "System Events"
                    activate
                    display dialog "DōmAI needs to use {command} for security monitoring" ¬
                        buttons {{"Deny", "Allow"}} ¬
                        default button "Allow" ¬
                        with title "Command Permission Required"
                end tell
            """
            
            result = await self._run_command(["osascript", "-e", script])
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error requesting command permission: {str(e)}")
            return False
            
    async def _run_command(self, cmd: List[str]) -> asyncio.subprocess.Process:
        """Run command and return process"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            return process
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {str(e)}")
            raise
            
    async def _query_tcc_db(self, db_path: str, query: str, params: Tuple) -> Optional[Tuple]:
        """Query TCC database safely"""
        if not os.path.exists(db_path):
            return None
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            return result
            
        except sqlite3.Error as e:
            self.logger.error(f"TCC database query failed: {str(e)}")
            return None
            
    async def _load_granted_permissions(self):
        """Load currently granted permissions"""
        for name, perm in self.permissions.items():
            if await self.check_permission(name):
                self.granted_permissions.add(perm.type)
                
    async def _log_permission_grant(self, permission_name: str):
        """Log permission grant for auditing"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "permission": permission_name,
                "bundle_id": self.bundle_id,
                "user": os.getenv("USER"),
                "granted": True
            }
            
            self.logger.info(f"Permission granted: {json.dumps(log_entry)}")
            
        except Exception as e:
            self.logger.error(f"Error logging permission grant: {str(e)}")

    def get_required_permissions(self, feature: str) -> List[MacPermission]:
        """Get list of permissions required for a feature"""
        try:
            if feature == "network_monitor":
                return [
                    self.permissions["packet_capture"],
                    self.permissions["process_monitor"]
                ]
            elif feature == "disk_monitor":
                return [self.permissions["disk_monitor"]]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting required permissions: {str(e)}")
            return []