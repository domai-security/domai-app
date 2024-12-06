#!/usr/bin/env python3
"""
DōmAI Prototype
Demonstrates core innovations in security analysis and learning
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import subprocess
import threading
import queue
import json
import datetime
import asyncio
import logging
from typing import Dict, List, Optional

app = Flask(__name__)
socketio = SocketIO(app)

class SecurityMonitor:
    def __init__(self):
        self.active_processes = {}
        self.output_queues = {}
        self.command_templates = {
            'connections': {
                'command': 'netstat -tunapl',
                'friendly': 'Check for unusual connections',
                'description': 'Lists all active network connections',
                'learning_points': [
                    'Each line shows a network connection',
                    'Local and remote addresses are shown',
                    'State indicates connection status'
                ]
            },
            'traffic': {
                'command': 'tcpdump -i any -n',
                'friendly': 'Monitor network traffic',
                'description': 'Captures and analyzes network packets',
                'learning_points': [
                    'Each line represents a packet',
                    'Source and destination IPs are shown',
                    'Protocol details are included'
                ]
            },
            'listening': {
                'command': 'lsof -i -n -P | grep LISTEN',
                'friendly': 'Check for listening ports',
                'description': 'Shows programs accepting connections',
                'learning_points': [
                    'Programs waiting for connections',
                    'Port numbers indicate services',
                    'Compare against expected services'
                ]
            }
        }

    def start_monitoring(self, commands: List[str]):
        """Start security monitoring with specified commands"""
        for cmd_type in commands:
            if cmd_type not in self.command_templates:
                continue

            template = self.command_templates[cmd_type]
            cmd = template['command']

            # Create output queue
            queue_id = f"{cmd_type}_{datetime.datetime.now().timestamp()}"
            self.output_queues[queue_id] = queue.Queue()

            # Start process
            try:
                process = subprocess.Popen(
                    cmd.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                self.active_processes[queue_id] = process

                # Start output handler
                thread = threading.Thread(
                    target=self._handle_output,
                    args=(queue_id, process),
                    daemon=True
                )
                thread.start()

            except Exception as e:
                logging.error(f"Failed to start {cmd_type}: {str(e)}")

    def _handle_output(self, queue_id: str, process: subprocess.Popen):
        """Handle process output and generate dual-stream analysis"""
        cmd_type = queue_id.split('_')[0]
        template = self.command_templates[cmd_type]

        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    break

                # Generate dual-stream analysis
                analysis = self._analyze_output(line, template)

                # Put in queue
                self.output_queues[queue_id].put({
                    'raw': line.strip(),
                    'crisis': analysis['crisis'],
                    'knowledge': analysis['knowledge']
                })

        except Exception as e:
            logging.error(f"Error handling output: {str(e)}")

        finally:
            if queue_id in self.active_processes:
                del self.active_processes[queue_id]

    def _analyze_output(self, line: str, template: Dict) -> Dict:
        """Generate dual-stream analysis of output"""
        # TODO: Replace with actual LLM analysis
        return {
            'crisis': self._format_crisis(line, template),
            'knowledge': self._format_knowledge(line, template)
        }

    def _format_crisis(self, line: str, template: Dict) -> str:
        """Format crisis stream output"""
        # Basic parsing - will be replaced with LLM
        if 'LISTEN' in line:
            return f"Found listening port: {line.split()[8]}"
        elif 'SYN' in line:
            return f"New connection attempt: {line.split()[2]} -> {line.split()[4]}"
        return f"Analyzing {template['friendly'].lower()}..."

    def _format_knowledge(self, line: str, template: Dict) -> str:
        """Format knowledge stream output"""
        # Will be replaced with LLM-generated content
        for point in template['learning_points']:
            if point not in self._shown_learning_points:
                self._shown_learning_points.add(point)
                return point
        return ""

# Initialize monitor
monitor = SecurityMonitor()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_monitoring')
def handle_monitoring_start(data):
    """Start security monitoring"""
    try:
        commands = data.get('commands', [])
        monitor.start_monitoring(commands)
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@socketio.on('get_updates')
def handle_updates():
    """Send updates from all active monitors"""
    for queue_id, queue in monitor.output_queues.items():
        try:
            while not queue.empty():
                data = queue.get_nowait()
                emit('monitor_update', {
                    'queue_id': queue_id,
                    'data': data
                })
        except Exception as e:
            logging.error(f"Error sending updates: {str(e)}")

if __name__ == '__main__':
    socketio.run(app, debug=True)
