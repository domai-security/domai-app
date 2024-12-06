#!/usr/bin/env python3
"""
Dual Stream Core Implementation for DōmAI

Implements parallel crisis and knowledge streams with unified context.
Each security event/analysis maintains integrity across both streams
while presenting different aspects of the same information.

Author: Claude
Created: December 2024
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from collections import deque
import logging
import json

class StreamType(Enum):
    CRISIS = "crisis"  # Immediate security response
    KNOWLEDGE = "knowledge"  # Educational/contextual content

@dataclass
class SecurityContext:
    """Shared context between streams"""
    session_id: str
    timestamp: datetime
    user_level: str
    command_history: List[str]
    active_threats: List[Dict[str, Any]]
    learning_opportunities: List[str]

@dataclass
class StreamOutput:
    """Output structure for either stream"""
    content: str
    stream_type: StreamType
    context_id: str
    timestamp: datetime
    metadata: Dict[str, Any]
    priority: int = 0  # Higher numbers = more urgent

class DualStreamManager:
    """Manages parallel crisis and knowledge streams"""
    
    def __init__(self):
        self.current_context: Optional[SecurityContext] = None
        self.crisis_buffer = deque(maxlen=1000)
        self.knowledge_buffer = deque(maxlen=1000)
        self.shared_state: Dict[str, Any] = {}
        self.learning_history: List[Dict[str, Any]] = []

    async def process_security_event(self, event: Dict[str, Any], user_level: str) -> tuple[StreamOutput, StreamOutput]:
        """Process security event and generate dual-stream output"""
        try:
            # Update context
            self._update_context(event, user_level)

            # Generate stream outputs
            crisis_output = await self._generate_crisis_output(event)
            knowledge_output = await self._generate_knowledge_output(event)

            # Store in buffers
            self.crisis_buffer.append(crisis_output)
            self.knowledge_buffer.append(knowledge_output)

            # Track learning opportunities
            self._track_learning(event, knowledge_output)

            return crisis_output, knowledge_output

        except Exception as e:
            logging.error(f"Error processing security event: {str(e)}")
            return self._get_fallback_outputs()

    async def start_command_execution(self, command: str, friendly_name: str) -> tuple[StreamOutput, StreamOutput]:
        """Begin command execution with dual-stream output"""
        try:
            # Update command history
            if self.current_context:
                self.current_context.command_history.append(command)

            # Generate initial outputs
            crisis = StreamOutput(
                content=f"Executing: {friendly_name}...",
                stream_type=StreamType.CRISIS,
                context_id=self.current_context.session_id if self.current_context else "unknown",
                timestamp=datetime.now(),
                metadata={"command": command, "stage": "start"},
                priority=1
            )

            knowledge = StreamOutput(
                content=self._get_command_explanation(command),
                stream_type=StreamType.KNOWLEDGE,
                context_id=self.current_context.session_id if self.current_context else "unknown",
                timestamp=datetime.now(),
                metadata={"command": command, "stage": "explanation"},
                priority=0
            )

            return crisis, knowledge

        except Exception as e:
            logging.error(f"Error starting command execution: {str(e)}")
            return self._get_fallback_outputs()

    def _update_context(self, event: Dict[str, Any], user_level: str):
        """Update security context"""
        if not self.current_context:
            self.current_context = SecurityContext(
                session_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user_level=user_level,
                command_history=[],
                active_threats=[],
                learning_opportunities=[]
            )
        
        # Update threat tracking
        if event.get('severity', '').upper() in ['HIGH', 'CRITICAL']:
            self.current_context.active_threats.append({
                'type': event.get('type'),
                'details': event.get('details'),
                'timestamp': datetime.now()
            })

    async def _generate_crisis_output(self, event: Dict[str, Any]) -> StreamOutput:
        """Generate crisis stream output"""
        # TODO: Replace with actual LLM generation
        severity = event.get('severity', 'UNKNOWN').upper()
        if severity in ['HIGH', 'CRITICAL']:
            content = f"ALERT: {event.get('type')} detected! {event.get('details')}"
            priority = 2
        else:
            content = f"Monitoring: {event.get('type')} - {event.get('details')}"
            priority = 1

        return StreamOutput(
            content=content,
            stream_type=StreamType.CRISIS,
            context_id=self.current_context.session_id if self.current_context else "unknown",
            timestamp=datetime.now(),
            metadata={"event_type": event.get('type')},
            priority=priority
        )

    async def _generate_knowledge_output(self, event: Dict[str, Any]) -> StreamOutput:
        """Generate knowledge stream output"""
        # TODO: Replace with actual LLM generation
        content = self._get_educational_content(event.get('type'))
        
        return StreamOutput(
            content=content,
            stream_type=StreamType.KNOWLEDGE,
            context_id=self.current_context.session_id if self.current_context else "unknown",
            timestamp=datetime.now(),
            metadata={"event_type": event.get('type')},
            priority=0
        )

    def _track_learning(self, event: Dict[str, Any], knowledge_output: StreamOutput):
        """Track learning opportunities and user progression"""
        if not self.current_context:
            return

        # Record learning opportunity
        learning_event = {
            'timestamp': datetime.now(),
            'event_type': event.get('type'),
            'knowledge_shared': knowledge_output.content,
            'user_level': self.current_context.user_level
        }
        self.learning_history.append(learning_event)

        # Check for learning achievements
        self._check_learning_achievements()

    def _check_learning_achievements(self):
        """Check for learning achievements and level progression"""
        if not self.current_context:
            return

        # Example achievement checks
        knowledge_count = len(self.learning_history)
        if knowledge_count >= 10 and self.current_context.user_level == 'novice':
            self.current_context.learning_opportunities.append(
                "Ready for more advanced security concepts!"
            )

    def _get_command_explanation(self, command: str) -> str:
        """Get educational explanation of command"""
        # TODO: Replace with actual LLM-generated content
        explanations = {
            'tcpdump': "tcpdump captures and analyzes network packets in real-time...",
            'netstat': "netstat shows active network connections and listening ports...",
            'lsof': "lsof lists open files and the processes using them..."
        }
        
        for cmd, explanation in explanations.items():
            if cmd in command.lower():
                return explanation
        return "This command helps monitor system security..."

    def _get_educational_content(self, event_type: str) -> str:
        """Get educational content based on event type"""
        # TODO: Replace with actual LLM-generated content
        content_map = {
            'network_connection': "Network connections allow your computer to communicate...",
            'file_access': "File access monitoring helps detect unauthorized changes...",
            'process_launch': "Processes are programs running on your system..."
        }
        return content_map.get(event_type, "Understanding this helps improve system security...")

    def _get_fallback_outputs(self) -> tuple[StreamOutput, StreamOutput]:
        """Generate fallback outputs for error cases"""
        timestamp = datetime.now()
        context_id = self.current_context.session_id if self.current_context else "unknown"

        crisis = StreamOutput(
            content="Continuing security monitoring...",
            stream_type=StreamType.CRISIS,
            context_id=context_id,
            timestamp=timestamp,
            metadata={"error": True},
            priority=0
        )

        knowledge = StreamOutput(
            content="Security monitoring helps protect your system...",
            stream_type=StreamType.KNOWLEDGE,
            context_id=context_id,
            timestamp=timestamp,
            metadata={"error": True},
            priority=0
        )

        return crisis, knowledge
