from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from domai_core import DōmAICore, SecurityProficiency, StreamOutput
import asyncio
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize core system
core = DōmAICore()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user_query')
async def handle_query(data):
    """Handle user's security query"""
    query = data['query']
    try:
        # Get user's current proficiency
        proficiency = core.user_partnership.get_communication_level()
        
        # Process query through AI Guardian
        output = await core.ai_guardian.process_user_query(query, proficiency)
        
        # Emit separate streams
        emit('crisis_update', {
            'content': output.crisis,
            'timestamp': output.timestamp.isoformat(),
            'session': output.context_id
        })
        
        emit('knowledge_update', {
            'content': output.knowledge,
            'timestamp': output.timestamp.isoformat(),
            'session': output.context_id
        })
        
        return {'status': 'success'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@socketio.on('security_event')
async def handle_security_event(data):
    """Handle incoming security events"""
    try:
        event = data['event']
        analysis, stream_output = await core.ai_guardian.analyze_security_event(event)
        
        if stream_output:
            emit('crisis_update', {
                'content': stream_output.crisis,
                'timestamp': stream_output.timestamp.isoformat(),
                'session': stream_output.context_id
            })
            
            emit('knowledge_update', {
                'content': stream_output.knowledge,
                'timestamp': stream_output.timestamp.isoformat(),
                'session': stream_output.context_id
            })
        
        return {'status': 'success'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    # Initialize the core system
    core.initialize()
    socketio.run(app, debug=True)
