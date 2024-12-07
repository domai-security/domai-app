#!/usr/bin/env python3
"""
API Routes for DōmAI

Handles web interface communication with core security systems.
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit
from typing import Dict, Any
import asyncio
import logging

from ..core.streams import DualStreamManager
from ..core.command_executor import CommandExecutor

api = Blueprint('api', __name__)

# Initialize core components
stream_manager = DualStreamManager()
command_executor = CommandExecutor(stream_manager)

@api.route('/query', methods=['POST'])
async def process_query():
    """Process natural language security query"""
    try:
        data = request.get_json()
        query = data.get('query')
        user_level = data.get('userLevel', 'novice')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        # Generate security plan
        # TODO: Use LLM to determine appropriate commands
        commands = ['network_listen', 'packet_capture']

        return jsonify({
            'status': 'success',
            'plan': {
                'commands': [
                    {
                        'type': cmd,
                        'friendly': command_executor.COMMAND_TEMPLATES[cmd].friendly_name,
                        'command': command_executor.COMMAND_TEMPLATES[cmd].command,
                        'description': command_executor.COMMAND_TEMPLATES[cmd].description
                    }
                    for cmd in commands
                ],
                'countdownSeconds': 5
            }
        })

    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        return jsonify({'error': 'An internal error has occurred!'}), 500

@api.route('/execute', methods=['POST'])
async def start_execution():
    """Start security command execution"""
    try:
        data = request.get_json()
        commands = data.get('commands', [])
        user_level = data.get('userLevel', 'novice')

        if not commands:
            return jsonify({'error': 'No commands provided'}), 400

        # Start command execution and streaming
        for cmd_type in commands:
            asyncio.create_task(stream_command_output(cmd_type))

        return jsonify({'status': 'success'})

    except Exception as e:
        logging.error(f"Error starting execution: {str(e)}")
        return jsonify({'error': 'An internal error has occurred!'}), 500

async def stream_command_output(command_type: str):
    """Stream command output through websockets"""
    try:
        async for crisis, knowledge in command_executor.execute_command(command_type):
            # Emit to appropriate streams
            emit('crisis_stream', {
                'content': crisis.content,
                'timestamp': crisis.timestamp.isoformat(),
                'metadata': crisis.metadata
            })

            emit('knowledge_stream', {
                'content': knowledge.content,
                'timestamp': knowledge.timestamp.isoformat(),
                'metadata': knowledge.metadata
            })

    except Exception as e:
        logging.error(f"Error streaming output: {str(e)}")
        emit('error', {'message': 'An internal error has occurred!'})

@api.route('/stop', methods=['POST'])
def stop_execution():
    """Stop all active security commands"""
    try:
        # Stop all active commands
        for command_id in list(command_executor.active_processes.keys()):
            command_executor.stop_command(command_id)

        return jsonify({'status': 'success'})

    except Exception as e:
        logging.error(f"Error stopping execution: {str(e)}")
        return jsonify({'error': 'An internal error has occurred!'}), 500

@api.route('/progress', methods=['GET'])
def get_learning_progress():
    """Get user's learning progress"""
    try:
        if not stream_manager.current_context:
            return jsonify({'error': 'No active session'}), 404

        return jsonify({
            'userLevel': stream_manager.current_context.user_level,
            'commandHistory': stream_manager.current_context.command_history,
            'learningOpportunities': stream_manager.current_context.learning_opportunities,
            'activeThreats': stream_manager.current_context.active_threats
        })

    except Exception as e:
        logging.error(f"Error getting progress: {str(e)}")
        return jsonify({'error': 'An internal error has occurred!'}), 500
