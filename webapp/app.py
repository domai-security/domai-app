from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from modules.packet_capture.tcpdump_monitor import TcpdumpMonitor, PacketData, ExplanationTier
from typing import Dict, Any
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
socketio = SocketIO(app)

# Global monitor instance
tcpdump_monitor = TcpdumpMonitor()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_capture')
def handle_capture_start(data):
    """Start packet capture based on user request"""
    try:
        tcpdump_monitor.start()
        # Register callback for packet processing
        tcpdump_monitor.add_callback('packet', lambda p: emit('packet_data', _format_packet(p)))
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@socketio.on('stop_capture')
def handle_capture_stop():
    tcpdump_monitor.stop()
    return {'status': 'success'}

@app.route('/api/analyze', methods=['POST'])
def analyze_query():
    """Handle natural language analysis requests"""
    query = request.json.get('query')
    # TODO: Implement LLM query processing
    # For now, return placeholder response
    return jsonify({
        'response': 'I understand you want to check your network traffic. Let me start monitoring...',
        'command': 'tcpdump -i any -n',
        'action': 'start_capture'
    })

def _format_packet(packet: PacketData) -> Dict[str, Any]:
    """Format packet data for frontend display"""
    return {
        'timestamp': packet.timestamp.isoformat(),
        'raw': packet.raw_output,
        'novice_explanation': tcpdump_monitor.get_explanation(packet, ExplanationTier.NOVICE),
        'apprentice_explanation': tcpdump_monitor.get_explanation(packet, ExplanationTier.APPRENTICE),
        'guardian_explanation': tcpdump_monitor.get_explanation(packet, ExplanationTier.GUARDIAN),
        'metadata': {
            'protocol': packet.protocol,
            'src_ip': packet.src_ip,
            'dst_ip': packet.dst_ip,
            'src_port': packet.src_port,
            'dst_port': packet.dst_port,
            'length': packet.length
        }
    }

if __name__ == '__main__':
    socketio.run(app, debug=True)
