#!/usr/bin/env python3
"""
DōmAI LLM Integration Module
Handles real-time natural language analysis of security events
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import logging

@dataclass
class SecurityContext:
    """Context information for security event analysis"""
    event_history: List[dict]
    user_proficiency: str
    system_state: dict
    threat_context: dict

@dataclass
class AnalysisResult:
    """Result of LLM analysis of security events"""
    explanation: str
    technical_details: dict
    severity: str
    recommendations: List[str]
    learning_points: List[str]

class LLMSecurityAnalyzer:
    """Core LLM-based security analysis engine"""
    def __init__(self, model_config: dict = None):
        self.context_window = deque(maxlen=100)  # Keep last 100 events for context
        self.analysis_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.prompt_templates = self._load_prompt_templates()
        
    def analyze_tcpdump(self, raw_output: str, context: SecurityContext) -> AnalysisResult:
        """Analyze tcpdump output with appropriate context"""
        prompt = self._build_tcpdump_prompt(raw_output, context)
        return self._get_llm_analysis(prompt, 'tcpdump')
    
    def analyze_system_log(self, log_entry: str, context: SecurityContext) -> AnalysisResult:
        """Analyze system log entries with context"""
        prompt = self._build_syslog_prompt(log_entry, context)
        return self._get_llm_analysis(prompt, 'syslog')
    
    def analyze_network_traffic(self, traffic_data: dict, context: SecurityContext) -> AnalysisResult:
        """Analyze network traffic patterns"""
        prompt = self._build_network_prompt(traffic_data, context)
        return self._get_llm_analysis(prompt, 'network')

    def explain_security_event(self, event: dict, context: SecurityContext) -> AnalysisResult:
        """Generate user-appropriate explanation of security events"""
        # Adapt explanation complexity to user proficiency
        proficiency_level = context.user_proficiency
        prompt = self._build_explanation_prompt(event, proficiency_level)
        return self._get_llm_analysis(prompt, 'explanation')
    
    def _build_tcpdump_prompt(self, raw_output: str, context: SecurityContext) -> str:
        """Build context-aware prompt for tcpdump analysis"""
        template = self.prompt_templates['tcpdump']
        return template.format(
            user_level=context.user_proficiency,
            recent_events=json.dumps(context.event_history[-5:]),
            raw_output=raw_output
        )
    
    def _build_syslog_prompt(self, log_entry: str, context: SecurityContext) -> str:
        """Build context-aware prompt for syslog analysis"""
        template = self.prompt_templates['syslog']
        return template.format(
            user_level=context.user_proficiency,
            system_state=json.dumps(context.system_state),
            log_entry=log_entry
        )
    
    def _build_network_prompt(self, traffic_data: dict, context: SecurityContext) -> str:
        """Build context-aware prompt for network analysis"""
        template = self.prompt_templates['network']
        return template.format(
            user_level=context.user_proficiency,
            threat_context=json.dumps(context.threat_context),
            traffic_data=json.dumps(traffic_data)
        )
    
    def _build_explanation_prompt(self, event: dict, proficiency_level: str) -> str:
        """Build user-appropriate explanation prompt"""
        template = self.prompt_templates['explanation']
        return template.format(
            proficiency_level=proficiency_level,
            event=json.dumps(event)
        )
    
    def _get_llm_analysis(self, prompt: str, analysis_type: str) -> AnalysisResult:
        """Get LLM analysis while handling caching and errors"""
        # Check cache first
        cache_key = hash(prompt)
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        try:
            # TODO: Implement actual LLM call here
            # For now, return placeholder
            result = AnalysisResult(
                explanation="Placeholder explanation",
                technical_details={},
                severity="INFO",
                recommendations=[],
                learning_points=[]
            )
            
            # Cache the result
            self.analysis_cache[cache_key] = result
            return result
            
        except Exception as e:
            logging.error(f"LLM analysis failed: {str(e)}")
            return self._get_fallback_analysis(analysis_type)
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different analysis types"""
        return {
            'tcpdump': """Given the following tcpdump output and context, provide a {user_level} level analysis:
                        Recent events: {recent_events}
                        Raw output: {raw_output}""",
            'syslog': """Analyze this system log entry for a {user_level} user:
                        System state: {system_state}
                        Log entry: {log_entry}""",
            'network': """Analyze this network traffic for a {user_level} user:
                        Threat context: {threat_context}
                        Traffic data: {traffic_data}""",
            'explanation': """Explain this security event for a {proficiency_level} user:
                        Event: {event}"""
        }
    
    def _get_fallback_analysis(self, analysis_type: str) -> AnalysisResult:
        """Provide fallback analysis when LLM fails"""
        return AnalysisResult(
            explanation=f"Basic {analysis_type} analysis (LLM unavailable)",
            technical_details={},
            severity="INFO",
            recommendations=["Monitor system for further events"],
            learning_points=["Security analysis temporarily limited"]
        )

class LLMIntegration:
    """Integration with DōmAI core system"""
    def __init__(self, core_system):
        self.core = core_system
        self.analyzer = LLMSecurityAnalyzer()
        self.active = False
        
    def start(self):
        """Start LLM integration"""
        self.active = True
        
    def stop(self):
        """Stop LLM integration"""
        self.active = False
        
    def handle_security_event(self, event: dict) -> AnalysisResult:
        """Handle security events with LLM analysis"""
        if not self.active:
            return None
            
        context = self._build_context(event)
        return self.analyzer.explain_security_event(event, context)
    
    def _build_context(self, event: dict) -> SecurityContext:
        """Build context for LLM analysis"""
        return SecurityContext(
            event_history=list(self.analyzer.context_window),
            user_proficiency=self.core.user_partnership.get_communication_level(),
            system_state=self._get_system_state(),
            threat_context=self._get_threat_context()
        )
    
    def _get_system_state(self) -> dict:
        """Get current system state"""
        return {
            'protection_level': self.core.protection_dome.protection_level,
            'shields': self.core.protection_dome.shields,
            'monitoring_active': self.core.protection_dome.monitoring_active
        }
    
    def _get_threat_context(self) -> dict:
        """Get current threat context"""
        return {
            'threat_database': self.core.ai_guardian.threat_database,
            'behavioral_analysis': self.core.ai_guardian.behavioral_analysis
        }
