#!/usr/bin/env python3
"""
Core security types for DōmAI
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any

class SecurityLevel(Enum):
    BASIC = auto()
    STANDARD = auto()
    ENHANCED = auto()
    MAXIMUM = auto()

class UserLevel(Enum):
    NOVICE = "Friendly Guide"
    APPRENTICE = "Security Partner"
    GUARDIAN = "Security Expert"
    SENTINEL = "Security Architect"

@dataclass
class SecurityEvent:
    id: str
    timestamp: datetime
    event_type: str
    severity: SecurityLevel
    source: str
    raw_data: str
    metadata: Dict[str, Any]
    context: Dict[str, Any] = None

@dataclass
class StreamOutput:
    crisis: str
    knowledge: str
    timestamp: datetime
    source: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class SecurityContext:
    session_id: str
    user_level: UserLevel
    active_monitors: List[str]
    threat_level: SecurityLevel
    system_state: Dict[str, Any]
    last_updated: datetime