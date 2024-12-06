#!/usr/bin/env python3
"""
Tcpdump Monitor Module for DōmAI
Author: Claude Desktop AI
Purpose: Provides real-time packet capture and analysis with multi-tiered explanation
"""

import subprocess
import threading
import queue
import json
import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class ExplanationTier(Enum):
    RAW = "raw"  # Always available
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    GUARDIAN = "guardian"
    SENTINEL = "sentinel"  # Future: Full security expert view

@dataclass
class PacketData:
    """Raw and analyzed packet data"""
    timestamp: datetime.datetime
    raw_output: str
    protocol: str
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    length: Optional[int]
    flags: Optional[Dict[str, bool]]
    # Future fields for enhanced analysis
    metadata: Dict[str, any] = None
    threats: List[Dict[str, any]] = None
    context: Dict[str, any] = None

class TcpdumpMonitor:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.packet_queue = queue.Queue()
        self.callbacks: Dict[str, List[Callable]] = {}
        self.running = False
        self.current_interface = None
        self.current_filter = None
        
        # Placeholder for future features
        self.llm_analyzer = None  # Future: LLM-based packet analysis
        self.threat_detector = None  # Future: Real-time threat detection
        self.pattern_analyzer = None  # Future: Traffic pattern analysis
        
    def start(self, interface: str = "any", packet_filter: str = ""):
        """Start packet capture with optional interface and filter"""
        if self.running:
            return
            
        self.current_interface = interface
        self.current_filter = packet_filter
        
        # Base tcpdump command with timestamp and verbose output
        cmd = [
            "sudo", "tcpdump",
            "-i", interface,
            "-tttt",  # Unix timestamp
            "-l",    # Line-buffered output
            "-n"     # Don't convert addresses
        ]
        
        if packet_filter:
            cmd.extend(["-vv", packet_filter])
            
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            self.running = True
            
            # Start processing threads
            self._start_monitor_threads()
            
        except Exception as e:
            raise RuntimeError(f"Failed to start tcpdump: {str(e)}")
            
    def stop(self):
        """Stop packet capture"""
        if not self.running:
            return
            
        self.running = False
        if self.process:
            self.process.terminate()
            self.process = None
            
    def add_callback(self, event_type: str, callback: Callable):
        """Register callback for specific event types"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
        
    def _start_monitor_threads(self):
        """Start monitoring threads for packet processing"""
        # Thread for reading tcpdump output
        threading.Thread(
            target=self._read_output,
            daemon=True
        ).start()
        
        # Thread for processing packets
        threading.Thread(
            target=self._process_packets,
            daemon=True
        ).start()
        
    def _read_output(self):
        """Read and queue tcpdump output"""
        while self.running and self.process:
            line = self.process.stdout.readline()
            if not line:
                break
                
            self.packet_queue.put(line.strip())
            
    def _process_packets(self):
        """Process packets from queue"""
        while self.running:
            try:
                raw_packet = self.packet_queue.get(timeout=1)
                packet_data = self._parse_packet(raw_packet)
                
                # Notify callbacks
                self._notify_callbacks("packet", packet_data)
                
                # Future: Threat detection
                if self.threat_detector:
                    threats = self.threat_detector.analyze(packet_data)
                    if threats:
                        self._notify_callbacks("threat", threats)
                        
                # Future: Pattern analysis
                if self.pattern_analyzer:
                    patterns = self.pattern_analyzer.update(packet_data)
                    if patterns:
                        self._notify_callbacks("pattern", patterns)
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing packet: {str(e)}")
                
    def _parse_packet(self, raw_output: str) -> PacketData:
        """Parse raw tcpdump output into structured data"""
        # Basic parsing - will be enhanced in future
        try:
            # Example line:
            # 2024-03-14 15:04:32.123456 IP 192.168.1.100.63572 > 10.0.0.1.443: tcp 52
            parts = raw_output.split()
            timestamp_str = f"{parts[0]} {parts[1]}"
            timestamp = datetime.datetime.strptime(
                timestamp_str,
                "%Y-%m-%d %H:%M:%S.%f"
            )
            
            protocol = parts[2]
            src = parts[3].split(".")
            dst = parts[5].split(".")
            
            return PacketData(
                timestamp=timestamp,
                raw_output=raw_output,
                protocol=protocol,
                src_ip=".".join(src[:-1]),
                dst_ip=".".join(dst[:-1]),
                src_port=int(src[-1]),
                dst_port=int(dst[-1]),
                length=int(parts[-1]) if parts[-1].isdigit() else None,
                flags=None,  # Future: Parse TCP flags
                metadata={},  # Future: Enhanced metadata
                threats=[],   # Future: Threat indicators
                context={}    # Future: Contextual information
            )
            
        except Exception as e:
            print(f"Error parsing packet: {str(e)}")
            return PacketData(
                timestamp=datetime.datetime.now(),
                raw_output=raw_output,
                protocol="UNKNOWN",
                src_ip="",
                dst_ip="",
                src_port=None,
                dst_port=None,
                length=None,
                flags=None
            )
            
    def _notify_callbacks(self, event_type: str, data: any):
        """Notify registered callbacks of events"""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in callback: {str(e)}")
                    
    def get_explanation(self, packet: PacketData, tier: ExplanationTier) -> str:
        """Get tiered explanation of packet data"""
        if tier == ExplanationTier.RAW:
            return packet.raw_output
            
        # Basic tiered explanations - will be replaced with LLM
        if tier == ExplanationTier.NOVICE:
            if packet.dst_port == 443:
                return f"Secure web connection to {packet.dst_ip}"
            elif packet.dst_port == 80:
                return f"Web connection to {packet.dst_ip}"
            return f"Network connection to {packet.dst_ip}"
            
        elif tier == ExplanationTier.APPRENTICE:
            return (
                f"{packet.protocol} connection from {packet.src_ip}:{packet.src_port} "
                f"to {packet.dst_ip}:{packet.dst_port}"
            )
            
        elif tier == ExplanationTier.GUARDIAN:
            # Future: Enhanced technical explanation
            return packet.raw_output
            
        return packet.raw_output  # Default to raw
