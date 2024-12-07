#!/usr/bin/env python3
"""
LLM integration for security analysis and explanation
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime

from ..core.types.security import SecurityEvent, UserLevel
from .types import AnalysisRequest, AnalysisResponse, StreamType
from .prompts import PROMPT_TEMPLATES

class LLMAnalyzer:
    def __init__(self):
        self.context_window = []
        self.analysis_cache = {}
        
    async def analyze_event(self, event: SecurityEvent, user_level: UserLevel) -> Dict[str, str]:
        """Analyze security event and generate dual-stream output"""
        # Update context window
        self.context_window.append({
            'timestamp': event.timestamp,
            'type': event.event_type,
            'severity': event.severity
        })
        
        # Trim context window if needed
        if len(self.context_window) > 100:
            self.context_window = self.context_window[-100:]
            
        # Prepare analysis request
        request = AnalysisRequest(
            event=event,
            user_level=user_level,
            context_window=self.context_window,
            stream_types=[StreamType.CRISIS, StreamType.KNOWLEDGE]
        )
        
        # Check cache
        cache_key = self._get_cache_key(request)
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
            
        # Generate analysis
        analysis = await self._generate_analysis(request)
        
        # Cache result
        self.analysis_cache[cache_key] = {
            'crisis': analysis.crisis_output,
            'knowledge': analysis.knowledge_output
        }
        
        return {
            'crisis': analysis.crisis_output,
            'knowledge': analysis.knowledge_output
        }
        
    def _get_cache_key(self, request: AnalysisRequest) -> str:
        """Generate cache key for analysis request"""
        return f"{request.event.id}:{request.user_level.value}"
        
    async def _generate_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """Generate analysis using LLM"""
        # TODO: Replace with actual LLM integration
        crisis_prompt = PROMPT_TEMPLATES['crisis'].format(
            event=request.event.raw_data,
            user_level=request.user_level.value
        )
        
        knowledge_prompt = PROMPT_TEMPLATES['knowledge'].format(
            event=request.event.raw_data,
            user_level=request.user_level.value,
            context=self.context_window[-5:]
        )
        
        # Placeholder responses
        return AnalysisResponse(
            crisis_output=self._format_crisis_output(request.event),
            knowledge_output=self._format_knowledge_output(request.event),
            timestamp=datetime.now()
        )
        
    def _format_crisis_output(self, event: SecurityEvent) -> str:
        """Format crisis stream output"""
        if event.severity.value >= 3:  # ENHANCED or MAXIMUM
            return f"ALERT: High severity {event.event_type} detected"
        return f"Monitoring: {event.event_type}"
        
    def _format_knowledge_output(self, event: SecurityEvent) -> str:
        """Format knowledge stream output"""
        return f"Understanding {event.event_type}:\n" + \
               f"This type of event indicates network activity..."