#!/usr/bin/env python3
"""
DōmAI Dual-Stream Manager
Handles bifurcated output streams while maintaining unified context

Author: Claude Desktop AI
Purpose: Core implementation of the dual-stream security analysis system
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json
from enum import Enum

class StreamType(Enum):
    CRISIS = "crisis"
    KNOWLEDGE = "knowledge"

@dataclass
class SecurityContext:
    """Unified context for both streams"""
    session_id: str
    start_time: datetime
    user_proficiency: str
    current_analysis: Dict[str, Any]
    command_history: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    learning_opportunities: List[Dict[str, Any]]

@dataclass
class StreamOutput:
    """Output for a specific stream"""
    stream_type: StreamType
    content: str
    timestamp: datetime
    context_id: str
    metadata: Dict[str, Any]

class DualStreamManager:
    """Manages bifurcated output streams while maintaining unified context"""
    
    def __init__(self):
        self.context = None
        self.crisis_handlers: List[Callable] = []
        self.knowledge_handlers: List[Callable] = []
        self.active_commands: Dict[str, asyncio.subprocess.Process] = {}
        self.output_buffer: Dict[StreamType, List[StreamOutput]] = {
            StreamType.CRISIS: [],
            StreamType.KNOWLEDGE: []
        }

    async def initialize_session(self, user_proficiency: str) -> str:
        """Initialize a new dual-stream session"""
        self.context = SecurityContext(
            session_id=str(uuid.uuid4()),
            start_time=datetime.now(),
            user_proficiency=user_proficiency,
            current_analysis={},
            command_history=[],
            findings=[],
            learning_opportunities=[]
        )
        return self.context.session_id

    async def process_user_input(self, query: str) -> Dict[str, Any]:
        """Process user input and update both streams"""
        try:
            # Get LLM analysis of user query
            analysis = await self._analyze_query(query)
            
            # Update security context
            self.context.current_analysis = analysis
            
            # Generate stream-specific outputs
            crisis_output = await self._generate_crisis_output(analysis)
            knowledge_output = await self._generate_knowledge_output(analysis)
            
            # Store outputs in buffer
            await self._buffer_output(StreamType.CRISIS, crisis_output)
            await self._buffer_output(StreamType.KNOWLEDGE, knowledge_output)
            
            # Notify handlers
            await self._notify_stream_handlers()
            
            return {
                'crisis': crisis_output,
                'knowledge': knowledge_output,
                'context': self.context
            }
            
        except Exception as e:
            logging.error(f"Error processing input: {str(e)}")
            raise

    async def execute_security_command(self, command: Dict[str, Any]) -> None:
        """Execute security command and process output"""
        try:
            # Add command to history
            self.context.command_history.append(command)
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *command['args'],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Track active command
            cmd_id = str(uuid.uuid4())
            self.active_commands[cmd_id] = process
            
            # Process output streams
            asyncio.create_task(self._handle_command_output(cmd_id, process))
            
        except Exception as e:
            await self._handle_command_error(command, e)

    async def _handle_command_output(self, cmd_id: str, process: asyncio.subprocess.Process) -> None:
        """Handle command output streams"""
        try:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                # Analyze output line
                analysis = await self._analyze_command_output(line.decode())
                
                # Generate stream outputs
                crisis_output = await self._generate_crisis_output(analysis)
                knowledge_output = await self._generate_knowledge_output(analysis)
                
                # Buffer outputs
                await self._buffer_output(StreamType.CRISIS, crisis_output)
                await self._buffer_output(StreamType.KNOWLEDGE, knowledge_output)
                
                # Notify handlers
                await self._notify_stream_handlers()
                
        except Exception as e:
            logging.error(f"Error handling command output: {str(e)}")
        finally:
            # Cleanup
            if cmd_id in self.active_commands:
                del self.active_commands[cmd_id]

    async def _analyze_command_output(self, output: str) -> Dict[str, Any]:
        """Analyze command output for both streams"""
        # TODO: Implement LLM analysis
        return {}

    async def _generate_crisis_output(self, analysis: Dict[str, Any]) -> StreamOutput:
        """Generate crisis-focused output"""
        # TODO: Implement crisis output generation
        return StreamOutput(
            stream_type=StreamType.CRISIS,
            content="",
            timestamp=datetime.now(),
            context_id=self.context.session_id,
            metadata={}
        )

    async def _generate_knowledge_output(self, analysis: Dict[str, Any]) -> StreamOutput:
        """Generate knowledge-focused output"""
        # TODO: Implement knowledge output generation
        return StreamOutput(
            stream_type=StreamType.KNOWLEDGE,
            content="",
            timestamp=datetime.now(),
            context_id=self.context.session_id,
            metadata={}
        )

    async def _buffer_output(self, stream_type: StreamType, output: StreamOutput) -> None:
        """Buffer stream output"""
        self.output_buffer[stream_type].append(output)
        
        # Maintain reasonable buffer size
        if len(self.output_buffer[stream_type]) > 1000:
            self.output_buffer[stream_type] = self.output_buffer[stream_type][-1000:]

    async def _notify_stream_handlers(self) -> None:
        """Notify registered handlers of new output"""
        crisis_handlers = [h(output) for h in self.crisis_handlers 
                         for output in self.output_buffer[StreamType.CRISIS]]
        knowledge_handlers = [h(output) for h in self.knowledge_handlers 
                            for output in self.output_buffer[StreamType.KNOWLEDGE]]
        
        await asyncio.gather(*crisis_handlers, *knowledge_handlers)

    def register_crisis_handler(self, handler: Callable) -> None:
        """Register handler for crisis stream"""
        self.crisis_handlers.append(handler)

    def register_knowledge_handler(self, handler: Callable) -> None:
        """Register handler for knowledge stream"""
        self.knowledge_handlers.append(handler)
