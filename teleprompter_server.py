#!/usr/bin/env python3
"""
Teleprompter Server for Interview Intelligence Platform
Provides API endpoints for teleprompter functionality
"""
from flask import Flask, jsonify, request, render_template_string
from teleprompter_integration import get_teleprompter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    """Main teleprompter interface"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Live Teleprompter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #00ff88;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            border-radius: 15px;
            padding: 20px;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .status {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .question-card {
            background: rgba(255, 107, 53, 0.1);
            border: 1px solid #ff6b35;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .question-card h3 {
            color: #ff6b35;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .response-card {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .response-card h3 {
            color: #00ff88;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .conversation-history {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .conversation-item {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
        }
        
        .interviewer {
            background: rgba(255, 107, 53, 0.2);
            border-left: 3px solid #ff6b35;
        }
        
        .assistant {
            background: rgba(0, 255, 136, 0.2);
            border-left: 3px solid #00ff88;
        }
        
        .timestamp {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        
        .audio-status {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .audio-active {
            background: #00ff88;
            animation: pulse 2s infinite;
        }
        
        .audio-inactive {
            background: #ff4444;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Live Teleprompter</h1>
            <p>AI-Powered Real-Time Interview Assistance</p>
        </div>
        
        <div class="status" id="status">
            <strong>Status:</strong> <span id="statusText">Connecting...</span>
            <div class="audio-status" id="audioStatus"></div>
        </div>
        
        <div class="question-card">
            <h3>🎤 Current Question</h3>
            <div id="currentQuestion">Waiting for question...</div>
        </div>
        
        <div class="response-card">
            <h3>💡 AI-Generated Response</h3>
            <div id="currentResponse">Waiting for response...</div>
        </div>
        
        <div class="conversation-history">
            <h3>📝 Conversation History</h3>
            <div id="conversationHistory">No conversation yet...</div>
        </div>
    </div>
    
    <script>
        let lastUpdate = null;
        
        function updateStatus(text) {
            document.getElementById('statusText').textContent = text;
        }
        
        function updateAudioStatus(listening) {
            const statusElement = document.getElementById('audioStatus');
            if (listening) {
                statusElement.className = 'audio-status audio-active';
                statusElement.title = 'Audio listening active';
            } else {
                statusElement.className = 'audio-status audio-inactive';
                statusElement.title = 'Audio listening inactive';
            }
        }
        
        function updateQuestion(question) {
            document.getElementById('currentQuestion').textContent = question || 'Waiting for question...';
        }
        
        function updateResponse(response) {
            document.getElementById('currentResponse').textContent = response || 'Waiting for response...';
        }
        
        function updateConversationHistory(history) {
            const container = document.getElementById('conversationHistory');
            if (!history || history.length === 0) {
                container.innerHTML = 'No conversation yet...';
                return;
            }
            
            container.innerHTML = history.map(item => `
                <div class="conversation-item ${item.speaker}">
                    <strong>${item.speaker === 'interviewer' ? '🎤 Interviewer' : '🤖 AI Assistant'}:</strong>
                    <div>${item.text}</div>
                    <div class="timestamp">${new Date(item.timestamp).toLocaleTimeString()}</div>
                </div>
            `).join('');
            
            container.scrollTop = container.scrollHeight;
        }
        
        async function fetchData() {
            try {
                const response = await fetch('/api/response');
                const data = await response.json();
                
                if (data.timestamp !== lastUpdate) {
                    lastUpdate = data.timestamp;
                    updateQuestion(data.question);
                    updateResponse(data.response);
                    updateStatus('Connected - AI Response Generation Active');
                }
                
                // Fetch conversation history
                const historyResponse = await fetch('/api/conversation');
                const historyData = await historyResponse.json();
                updateConversationHistory(historyData);
                
                // Fetch status
                const statusResponse = await fetch('/api/status');
                const statusData = await statusResponse.json();
                updateAudioStatus(statusData.is_listening);
                
            } catch (error) {
                updateStatus('Connection error - Retrying...');
                console.error('Error fetching data:', error);
            }
        }
        
        // Auto-refresh every 2 seconds
        setInterval(fetchData, 2000);
        
        // Initial load
        fetchData();
    </script>
</body>
</html>
""")

@app.route('/api/start', methods=['POST'])
def start_teleprompter():
    """Start the teleprompter"""
    data = request.get_json() or {}
    stealth_mode = data.get('stealth_mode', True)
    
    teleprompter = get_teleprompter()
    result = teleprompter.start_teleprompter(stealth_mode)
    
    return jsonify(result)

@app.route('/api/stop', methods=['POST'])
def stop_teleprompter():
    """Stop the teleprompter"""
    teleprompter = get_teleprompter()
    result = teleprompter.stop_teleprompter()
    
    return jsonify(result)

@app.route('/api/status')
def get_status():
    """Get teleprompter status"""
    teleprompter = get_teleprompter()
    return jsonify(teleprompter.get_status())

@app.route('/api/conversation')
def get_conversation():
    """Get conversation history"""
    teleprompter = get_teleprompter()
    return jsonify(teleprompter.get_conversation())

@app.route('/api/response')
def get_current_response():
    """Get current response"""
    teleprompter = get_teleprompter()
    return jsonify(teleprompter.get_current_response())

@app.route('/api/qr')
def generate_qr():
    """Generate QR code"""
    teleprompter = get_teleprompter()
    return jsonify(teleprompter.generate_qr_code())

if __name__ == '__main__':
    print("🎯 Starting Teleprompter Server...")
    print("📱 Mobile Interface: http://localhost:8081")
    print("🔗 QR Code: http://localhost:8081/api/qr")
    app.run(host='0.0.0.0', port=8081, debug=False)
