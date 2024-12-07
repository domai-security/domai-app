#!/usr/bin/env python3
"""
Tcpdump Monitor Module for DōmAI
Author: Claude
Purpose: Provides real-time packet capture and analysis with multi-tiered explanation
"""

import subprocess
import threading
import queue
import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class ExplanationTier(Enum):
    RAW = "raw"
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    GUARDIAN = "guardian"
    SENTINEL = "sentinel"

@dataclass
class PacketData:
    timestamp: datetime.datetime
    raw_output: str
    protocol: str
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    length: Optional[int]
    flags: Optional[Dict[str, bool]]
    metadata: Dict[str, any] = None
    threats: List[Dict[str, any]] = None
    context: Dict[str, any] = None

class TcpdumpMonitor:
    def __init__(self, permission_manager=None):
        self.process: Optional[subprocess.Popen] = None
        self.packet_queue = queue.Queue()
        self.callbacks: Dict[str, List[Callable]] = {}
        self.running = False
        self.current_interface = None
        self.current_filter = None
        self.permission_manager = permission_manager
        
    def _find_tcpdump(self) -> Optional[str]:
        """Find tcpdump binary in system"""
        common_paths = [
            "/usr/sbin/tcpdump",
            "/usr/local/sbin/tcpdump",
            "/opt/homebrew/bin/tcpdump"
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        return None

    def _build_command(self, interface: str, packet_filter: str) -> List[str]:
        """Build tcpdump command safely"""
        tcpdump_path = self._find_tcpdump()
        if not tcpdump_path:
            raise RuntimeError("tcpdump not found in system")
            
        cmd = [tcpdump_path]
        
        # Add base arguments
        cmd.extend([
            "-i", interface,
            "-tttt",  # Unix timestamp
            "-l",     # Line buffered
            "-n"      # Don't convert addresses
        ])
        
        if packet_filter:
            cmd.extend(["-vv", packet_filter])
            
        return cmd
        
    def start(self, interface: str = "any", packet_filter: str = ""):
        """Start packet capture with optional interface and filter"""
        if self.running:
            return
            
        self.current_interface = interface
        self.current_filter = packet_filter
        
        try:
            cmd = self._build_command(interface, packet_filter)
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.running = True
            self._start_monitor_threads()
            
        except Exception as e:
            raise RuntimeError(f"Failed to start tcpdump: {str(e)}")
            
    # ... [rest of the existing code remains unchanged]
