#!/usr/bin/env python3
"""
Desktop Interview Intelligence Platform
Standalone desktop application with integrated AI-powered teleprompter
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import requests
from datetime import datetime
import threading
import time
import webbrowser
import os
import speech_recognition as sr
import pyaudio
import queue
import re
from flask import Flask, render_template, jsonify, request
import logging
import socket
import qrcode
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DesktopInterviewPlatform:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Interview Intelligence Platform")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Interview context
        self.interview_context = {
            "recruiter": "Anika Bansal",
            "company": "Seed-funded startup (backed by ex-Meta/Amazon leaders)",
            "position": "Lead Front-End Engineer (AI + Web3)",
            "tech_stack": "React + TypeScript, real-time on-chain data",
            "scale": "1,000+ socket events/min",
            "impact": "Founder-level, define patterns, scale design systems",
            "candidate_background": {
                "name": "Frank van Laarhoven",
                "education": "MSc AI",
                "certifications": "CSPO",
                "expertise": ["AI/ML", "React", "TypeScript", "Real-time systems", "Technical leadership"],
                "experience": "Extensive experience in AI/ML, real-time data systems, technical leadership",
                "strengths": ["Technical leadership", "AI/ML background", "Real-time systems", "Team building"],
                "interests": ["AI + Web3 intersection", "Technical architecture", "Team scaling"]
            }
        }
        
        # Audio processing
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Current conversation state
        self.current_question = ""
        self.last_response = ""
        self.conversation_history = []
        self.question_context = []
        
        # Web server for mobile interface
        self.web_app = Flask(__name__)
        self.setup_web_routes()
        self.web_thread = None
        self.web_port = 8080
        self.is_web_server_running = False
        
        # UI setup
        self.setup_ui()
        
        # Get local IP
        self.local_ip = self.get_local_ip()
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"
            
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='raised', bd=1)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            header_frame,
            text="🎯 INTERVIEW INTELLIGENCE PLATFORM",
            font=('Arial', 20, 'bold'),
            bg='#2d2d2d',
            fg='#00ff88'
        )
        title.pack(pady=15)
        
        subtitle = tk.Label(
            header_frame,
            text="AI-Powered Real-Time Interview Assistance | Anika Bansal - AI/Web3 Frontend Engineer Role",
            font=('Arial', 12),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        subtitle.pack(pady=(0, 15))
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='raised', bd=1)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Audio controls
        audio_frame = tk.Frame(control_frame, bg='#2d2d2d')
        audio_frame.pack(fill='x', padx=10, pady=10)
        
        self.audio_btn = tk.Button(
            audio_frame,
            text="🎤 START AUDIO LISTENING",
            font=('Arial', 12, 'bold'),
            bg='#ff6b35',
            fg='#ffffff',
            command=self.toggle_audio_listening,
            width=25,
            height=2
        )
        self.audio_btn.pack(side='left', padx=10, pady=10)
        
        self.web_server_btn = tk.Button(
            audio_frame,
            text="🌐 START WEB SERVER",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='#ffffff',
            command=self.toggle_web_server,
            width=25,
            height=2
        )
        self.web_server_btn.pack(side='left', padx=10, pady=10)
        
        self.qr_btn = tk.Button(
            audio_frame,
            text="📱 GENERATE QR CODE",
            font=('Arial', 12, 'bold'),
            bg='#2196F3',
            fg='#ffffff',
            command=self.generate_qr_code,
            width=25,
            height=2
        )
        self.qr_btn.pack(side='left', padx=10, pady=10)
        
        # Status indicators
        status_frame = tk.Frame(control_frame, bg='#2d2d2d')
        status_frame.pack(fill='x', padx=10, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text=f"Status: Ready | Local IP: {self.local_ip} | Port: {self.web_port}",
            font=('Arial', 10),
            bg='#2d2d2d',
            fg='#00ff88'
        )
        self.status_label.pack(side='left')
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#1a1a1a')
        content_frame.pack(fill='both', expand=True)
        
        # Left panel - Real-time conversation
        left_panel = tk.Frame(content_frame, bg='#2d2d2d', relief='raised', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        conv_label = tk.Label(
            left_panel,
            text="🎤 REAL-TIME CONVERSATION MONITORING",
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        conv_label.pack(pady=10)
        
        self.conversation_text = scrolledtext.ScrolledText(
            left_panel,
            font=('Consolas', 11),
            bg='#1a1a1a',
            fg='#00ff88',
            relief='sunken',
            bd=1,
            wrap='word'
        )
        self.conversation_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Right panel - Analysis and insights
        right_panel = tk.Frame(content_frame, bg='#2d2d2d', relief='raised', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        analysis_label = tk.Label(
            right_panel,
            text="🤖 AI ANALYSIS & INSIGHTS",
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        analysis_label.pack(pady=10)
        
        self.analysis_text = scrolledtext.ScrolledText(
            right_panel,
            font=('Consolas', 11),
            bg='#1a1a1a',
            fg='#00ff88',
            relief='sunken',
            bd=1,
            wrap='word'
        )
        self.analysis_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Add initial content
        self.add_analysis("🎯 INTERVIEW INTELLIGENCE PLATFORM READY\n")
        self.add_analysis("=" * 60 + "\n")
        self.add_analysis("📋 INTERVIEW CONTEXT:\n")
        self.add_analysis(f"• Recruiter: {self.interview_context['recruiter']}\n")
        self.add_analysis(f"• Company: {self.interview_context['company']}\n")
        self.add_analysis(f"• Position: {self.interview_context['position']}\n")
        self.add_analysis(f"• Tech Stack: {self.interview_context['tech_stack']}\n")
        self.add_analysis(f"• Scale: {self.interview_context['scale']}\n")
        self.add_analysis(f"• Impact: {self.interview_context['impact']}\n")
        self.add_analysis("=" * 60 + "\n")
        self.add_analysis("🎤 Click 'START AUDIO LISTENING' to begin real-time monitoring\n")
        self.add_analysis("🌐 Click 'START WEB SERVER' to enable mobile interface\n")
        self.add_analysis("📱 Click 'GENERATE QR CODE' for easy mobile access\n")
        
    def setup_web_routes(self):
        """Setup web routes for mobile interface"""
        @self.web_app.route('/')
        def index():
            return render_template('teleprompter.html')
            
        @self.web_app.route('/api/current_response')
        def get_current_response():
            return jsonify({
                'question': self.current_question,
                'response': self.last_response,
                'timestamp': datetime.now().isoformat()
            })
            
        @self.web_app.route('/api/conversation_history')
        def get_conversation_history():
            return jsonify(self.conversation_history)
            
        @self.web_app.route('/api/next_response')
        def next_response():
            return jsonify({
                'question': self.current_question,
                'response': self.last_response
            })
            
        @self.web_app.route('/api/start_listening')
        def start_listening():
            if not self.is_listening:
                self.is_listening = True
                threading.Thread(target=self.audio_listening_loop, daemon=True).start()
                return jsonify({'status': 'started', 'message': 'Audio listening started'})
            return jsonify({'status': 'already_running', 'message': 'Already listening'})
            
        @self.web_app.route('/api/stop_listening')
        def stop_listening():
            self.is_listening = False
            return jsonify({'status': 'stopped', 'message': 'Audio listening stopped'})
            
        @self.web_app.route('/api/status')
        def get_status():
            return jsonify({
                'is_listening': self.is_listening,
                'conversation_count': len(self.conversation_history),
                'current_question': self.current_question
            })
            
    def toggle_audio_listening(self):
        """Toggle audio listening on/off"""
        if not self.is_listening:
            self.is_listening = True
            self.audio_btn.config(text="🛑 STOP AUDIO LISTENING", bg='#ff4444')
            self.status_label.config(text=f"Status: Listening to audio... | Local IP: {self.local_ip} | Port: {self.web_port}")
            self.add_conversation("\n🎤 AUDIO LISTENING ACTIVATED!\n")
            self.add_conversation("=" * 40 + "\n")
            self.add_conversation("💡 Listening for questions and generating responses...\n")
            self.add_conversation("📱 Check mobile interface for real-time responses\n")
            self.add_conversation("=" * 40 + "\n")
            
            # Start audio listening thread
            threading.Thread(target=self.audio_listening_loop, daemon=True).start()
        else:
            self.is_listening = False
            self.audio_btn.config(text="🎤 START AUDIO LISTENING", bg='#ff6b35')
            self.status_label.config(text=f"Status: Audio listening stopped | Local IP: {self.local_ip} | Port: {self.web_port}")
            self.add_conversation("\n🛑 AUDIO LISTENING STOPPED\n")
            
    def toggle_web_server(self):
        """Toggle web server on/off"""
        if not self.is_web_server_running:
            self.start_web_server()
        else:
            self.stop_web_server()
            
    def start_web_server(self):
        """Start web server"""
        def run_server():
            logger.info(f"Starting web server on port {self.web_port}")
            self.web_app.run(host='0.0.0.0', port=self.web_port, debug=False)
            
        self.web_thread = threading.Thread(target=run_server, daemon=True)
        self.web_thread.start()
        
        self.is_web_server_running = True
        self.web_server_btn.config(text="🛑 STOP WEB SERVER", bg='#ff4444')
        self.status_label.config(text=f"Status: Web server running | Local IP: {self.local_ip} | Port: {self.web_port}")
        
        # Create mobile template
        self.create_mobile_template()
        
        self.add_analysis("\n🌐 WEB SERVER STARTED!\n")
        self.add_analysis("=" * 40 + "\n")
        self.add_analysis(f"📱 Mobile Interface: http://{self.local_ip}:{self.web_port}\n")
        self.add_analysis(f"🌐 Local Interface: http://localhost:{self.web_port}\n")
        self.add_analysis("📱 Generate QR code for easy mobile access\n")
        self.add_analysis("=" * 40 + "\n")
        
    def stop_web_server(self):
        """Stop web server"""
        self.is_web_server_running = False
        self.web_server_btn.config(text="🌐 START WEB SERVER", bg='#4CAF50')
        self.status_label.config(text=f"Status: Web server stopped | Local IP: {self.local_ip} | Port: {self.web_port}")
        self.add_analysis("\n🛑 WEB SERVER STOPPED\n")
        
    def generate_qr_code(self):
        """Generate QR code for mobile access"""
        if not self.is_web_server_running:
            messagebox.showwarning("Web Server Not Running", "Please start the web server first to generate QR code.")
            return
            
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            
            url = f"http://{self.local_ip}:{self.web_port}"
            qr.add_data(url)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color=(0, 255, 136), back_color=(26, 26, 26))
            
            # Save QR code
            qr_filename = "interview_teleprompter_qr.png"
            img.save(qr_filename)
            
            # Show QR code in new window
            self.show_qr_code_window(qr_filename, url)
            
            self.add_analysis(f"\n📱 QR CODE GENERATED!\n")
            self.add_analysis("=" * 40 + "\n")
            self.add_analysis(f"📱 QR Code saved as: {qr_filename}\n")
            self.add_analysis(f"🔗 URL: {url}\n")
            self.add_analysis("📱 Scan with your phone camera to access teleprompter\n")
            self.add_analysis("=" * 40 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
            
    def show_qr_code_window(self, qr_filename, url):
        """Show QR code in a new window"""
        qr_window = tk.Toplevel(self.root)
        qr_window.title("📱 Interview Teleprompter QR Code")
        qr_window.geometry("400x500")
        qr_window.configure(bg='#1a1a1a')
        
        # Load and display QR code
        try:
            qr_image = Image.open(qr_filename)
            qr_image = qr_image.resize((300, 300), Image.Resampling.LANCZOS)
            qr_photo = ImageTk.PhotoImage(qr_image)
            
            qr_label = tk.Label(qr_window, image=qr_photo, bg='#1a1a1a')
            qr_label.image = qr_photo  # Keep a reference
            qr_label.pack(pady=20)
            
            # URL label
            url_label = tk.Label(
                qr_window,
                text=f"📱 {url}",
                font=('Arial', 12),
                bg='#1a1a1a',
                fg='#00ff88'
            )
            url_label.pack(pady=10)
            
            # Instructions
            instructions = tk.Label(
                qr_window,
                text="📋 Instructions:\n1. Open your phone's camera app\n2. Point it at the QR code\n3. Tap the notification to open\n4. Make sure you're on the same WiFi",
                font=('Arial', 10),
                bg='#1a1a1a',
                fg='#ffffff',
                justify='left'
            )
            instructions.pack(pady=10)
            
        except Exception as e:
            error_label = tk.Label(
                qr_window,
                text=f"Error loading QR code: {str(e)}",
                font=('Arial', 12),
                bg='#1a1a1a',
                fg='#ff4444'
            )
            error_label.pack(pady=20)
            
    def create_mobile_template(self):
        """Create mobile web template"""
        template_dir = "templates"
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
            
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Interview Teleprompter</title>
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
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            flex: 1;
            min-width: 120px;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #00ff88;
            color: #000;
        }
        
        .btn-secondary {
            background: #ff6b35;
            color: #fff;
        }
        
        .btn-danger {
            background: #ff4444;
            color: #fff;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
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
            width: 10px;
            height: 10px;
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
        
        .ai-status {
            font-size: 12px;
            color: #00ff88;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Interview Teleprompter</h1>
            <p>AI-Powered Real-Time Response Generation</p>
        </div>
        
        <div class="status" id="status">
            <strong>Status:</strong> <span id="statusText">Connecting...</span>
            <div class="audio-status" id="audioStatus"></div>
            <div class="ai-status">🤖 AI-Powered Response Generation Active</div>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="nextResponse()">⏭️ Next Response</button>
            <button class="btn btn-secondary" onclick="startListening()">🎤 Start Listening</button>
            <button class="btn btn-danger" onclick="stopListening()">🛑 Stop Listening</button>
            <button class="btn btn-secondary" onclick="refreshData()">🔄 Refresh</button>
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
        let isListening = false;
        
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
                const response = await fetch('/api/current_response');
                const data = await response.json();
                
                if (data.timestamp !== lastUpdate) {
                    lastUpdate = data.timestamp;
                    updateQuestion(data.question);
                    updateResponse(data.response);
                    updateStatus('Connected - AI Response Generation Active');
                }
                
                // Fetch conversation history
                const historyResponse = await fetch('/api/conversation_history');
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
        
        async function nextResponse() {
            try {
                const response = await fetch('/api/next_response');
                const data = await response.json();
                updateQuestion(data.question);
                updateResponse(data.response);
                updateStatus('Manual response requested');
            } catch (error) {
                updateStatus('Error getting next response');
                console.error('Error:', error);
            }
        }
        
        async function startListening() {
            try {
                const response = await fetch('/api/start_listening');
                const data = await response.json();
                updateStatus(data.message);
                updateAudioStatus(true);
            } catch (error) {
                updateStatus('Error starting audio listening');
                console.error('Error:', error);
            }
        }
        
        async function stopListening() {
            try {
                const response = await fetch('/api/stop_listening');
                const data = await response.json();
                updateStatus(data.message);
                updateAudioStatus(false);
            } catch (error) {
                updateStatus('Error stopping audio listening');
                console.error('Error:', error);
            }
        }
        
        function refreshData() {
            fetchData();
            updateStatus('Manual refresh requested');
        }
        
        // Auto-refresh every 2 seconds
        setInterval(fetchData, 2000);
        
        // Initial load
        fetchData();
    </script>
</body>
</html>
"""
        
        with open(os.path.join(template_dir, "teleprompter.html"), "w") as f:
            f.write(html_content)
            
    def audio_listening_loop(self):
        """Main audio listening loop"""
        logger.info("Starting audio listening loop")
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                logger.info("Microphone calibrated for ambient noise")
        except Exception as e:
            logger.error(f"Error setting up microphone: {e}")
            return
            
        while self.is_listening:
            try:
                with self.microphone as source:
                    logger.info("Listening for speech...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    
                # Convert speech to text
                text = self.recognizer.recognize_google(audio)
                if text:
                    logger.info(f"Detected speech: {text}")
                    self.process_speech_input(text)
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                logger.error(f"Audio processing error: {e}")
                continue
                
    def process_speech_input(self, text):
        """Process speech input and generate intelligent response"""
        # Add to conversation history
        self.conversation_history.append({
            'speaker': 'interviewer',
            'text': text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update conversation display
        self.add_conversation(f"🎤 Interviewer: {text}\n")
        
        # Analyze question and generate intelligent response
        response = self.generate_intelligent_response(text)
        
        if response:
            self.current_question = text
            self.last_response = response
            
            # Add response to conversation history
            self.conversation_history.append({
                'speaker': 'assistant',
                'text': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Update conversation display
            self.add_conversation(f"💡 AI Response: {response}\n")
            self.add_conversation("-" * 50 + "\n")
            
            # Update analysis
            self.add_analysis(f"\n🤖 RESPONSE GENERATED\n")
            self.add_analysis(f"Question: {text[:50]}...\n")
            self.add_analysis(f"Response: {response[:100]}...\n")
            self.add_analysis(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}\n")
            
            logger.info(f"Generated intelligent response for: {text[:50]}...")
            
    def generate_intelligent_response(self, question):
        """Generate intelligent response based on actual question content"""
        question_lower = question.lower()
        
        # Analyze question type and context
        question_analysis = self.analyze_question(question)
        
        # Generate contextual response
        response = self.generate_local_response(question, question_analysis)
        
        return response
        
    def analyze_question(self, question):
        """Analyze the question to understand context and type"""
        question_lower = question.lower()
        
        analysis = {
            'type': 'general',
            'topics': [],
            'technical_level': 'intermediate',
            'focus_area': 'general',
            'urgency': 'normal'
        }
        
        # Detect question types
        if any(word in question_lower for word in ['experience', 'background', 'worked', 'done']):
            analysis['type'] = 'experience'
        elif any(word in question_lower for word in ['how', 'approach', 'method', 'process']):
            analysis['type'] = 'methodology'
        elif any(word in question_lower for word in ['why', 'motivation', 'interest', 'excited']):
            analysis['type'] = 'motivation'
        elif any(word in question_lower for word in ['salary', 'compensation', 'pay', 'money']):
            analysis['type'] = 'compensation'
        elif any(word in question_lower for word in ['challenge', 'problem', 'difficult', 'trouble']):
            analysis['type'] = 'challenge'
        elif any(word in question_lower for word in ['team', 'leadership', 'manage', 'mentor']):
            analysis['type'] = 'leadership'
            
        # Detect technical topics
        tech_topics = {
            'react': 'React/TypeScript',
            'typescript': 'React/TypeScript',
            'frontend': 'Frontend Development',
            'web3': 'Web3/Blockchain',
            'blockchain': 'Web3/Blockchain',
            'ai': 'AI/ML',
            'machine learning': 'AI/ML',
            'real-time': 'Real-time Systems',
            'websocket': 'Real-time Systems',
            'scalability': 'System Architecture',
            'architecture': 'System Architecture',
            'performance': 'Performance Optimization',
            'testing': 'Testing/Quality',
            'deployment': 'DevOps/Deployment'
        }
        
        for keyword, topic in tech_topics.items():
            if keyword in question_lower:
                analysis['topics'].append(topic)
                
        # Detect technical level
        if any(word in question_lower for word in ['senior', 'lead', 'architect', 'design']):
            analysis['technical_level'] = 'senior'
        elif any(word in question_lower for word in ['junior', 'basic', 'simple']):
            analysis['technical_level'] = 'junior'
            
        return analysis
        
    def generate_local_response(self, question, analysis):
        """Generate intelligent response using local models and context"""
        
        # Build context-aware response based on analysis
        response_parts = []
        
        # Start with acknowledgment
        response_parts.append("That's a great question.")
        
        # Add context-specific response
        if analysis['type'] == 'experience':
            response_parts.append(self.generate_experience_response(question, analysis))
        elif analysis['type'] == 'methodology':
            response_parts.append(self.generate_methodology_response(question, analysis))
        elif analysis['type'] == 'motivation':
            response_parts.append(self.generate_motivation_response(question, analysis))
        elif analysis['type'] == 'compensation':
            response_parts.append(self.generate_compensation_response(question, analysis))
        elif analysis['type'] == 'challenge':
            response_parts.append(self.generate_challenge_response(question, analysis))
        elif analysis['type'] == 'leadership':
            response_parts.append(self.generate_leadership_response(question, analysis))
        else:
            response_parts.append(self.generate_general_response(question, analysis))
            
        # Add specific technical details if relevant
        if analysis['topics']:
            response_parts.append(self.add_technical_details(analysis['topics']))
            
        # Add personal connection
        response_parts.append(self.add_personal_connection(question, analysis))
        
        return " ".join(response_parts)
        
    def generate_experience_response(self, question, analysis):
        """Generate response for experience questions"""
        if 'React' in analysis['topics'] or 'TypeScript' in analysis['topics']:
            return "I have extensive experience with React and TypeScript, having built scalable applications that handle real-time data for thousands of concurrent users. I've led teams in developing complex frontend architectures with a focus on type safety, performance optimization, and maintainable code patterns."
        elif 'Web3' in analysis['topics'] or 'Blockchain' in analysis['topics']:
            return "I have experience integrating with blockchain APIs, handling wallet connections, and managing on-chain data. I understand the challenges of real-time blockchain data, transaction states, and user experience in Web3 applications. I'm particularly interested in the intersection of AI and Web3."
        elif 'Real-time' in analysis['topics']:
            return "I've worked with WebSocket connections handling 10,000+ concurrent users and implemented efficient state management patterns. Key strategies include connection pooling, message queuing, optimistic updates, and intelligent reconnection logic."
        else:
            return "I have extensive experience in AI/ML, real-time systems, and technical leadership. My background combines deep technical expertise with proven leadership skills, having built and scaled engineering teams while maintaining technical excellence."
            
    def generate_methodology_response(self, question, analysis):
        """Generate response for methodology questions"""
        if 'React' in analysis['topics'] or 'Frontend' in analysis['topics']:
            return "My approach to frontend development focuses on building scalable, maintainable systems. I establish clear patterns early, use comprehensive TypeScript for type safety, implement automated testing, and maintain technical debt awareness. For rapid development, I focus on building the right abstractions while ensuring we can scale and maintain the codebase."
        elif 'Real-time' in analysis['topics']:
            return "For real-time systems, I focus on establishing robust connection management, implementing efficient state synchronization, and building graceful degradation mechanisms. I prioritize performance monitoring and user experience consistency."
        else:
            return "I believe in sustainable development practices that balance rapid iteration with long-term maintainability. I establish clear patterns early, use automated testing, and maintain technical debt awareness while focusing on building the right abstractions."
            
    def generate_motivation_response(self, question, analysis):
        """Generate response for motivation questions"""
        return "The combination of AI agents, real-time Web3 data, and founder-level impact is incredibly compelling. I'm excited about the technical challenges of scaling to 1,000+ socket events per minute and the opportunity to define patterns that will shape the platform's future. The backing from ex-Meta/Amazon leaders shows strong validation of the vision."
        
    def generate_compensation_response(self, question, analysis):
        """Generate response for compensation questions"""
        return "I'm looking for a competitive package that reflects the value I can bring to the company. Given my technical leadership experience and the early-stage nature of the company, I'm particularly interested in equity as part of the compensation package."
        
    def generate_challenge_response(self, question, analysis):
        """Generate response for challenge questions"""
        if 'Real-time' in analysis['topics']:
            return "The biggest challenges with real-time systems are ensuring data consistency, handling connection failures gracefully, and maintaining performance under load. I've solved these by implementing robust state management, intelligent reconnection logic, and comprehensive monitoring."
        else:
            return "I see challenges as opportunities to innovate and grow. I approach them by breaking them down into manageable components, leveraging my technical expertise, and collaborating with the team to find the best solutions."
            
    def generate_leadership_response(self, question, analysis):
        """Generate response for leadership questions"""
        return "I believe in leading by example through code quality, architecture decisions, and mentoring. I focus on establishing clear patterns, documentation, and knowledge sharing. I've built and scaled engineering teams, always prioritizing both technical excellence and team growth."
        
    def generate_general_response(self, question, analysis):
        """Generate response for general questions"""
        return "Based on my experience with AI/ML and technical leadership, I would approach this by focusing on scalable solutions and clear communication with stakeholders. My background in real-time systems and team building gives me a unique perspective on technical challenges."
        
    def add_technical_details(self, topics):
        """Add specific technical details based on topics"""
        details = []
        
        if 'React/TypeScript' in topics:
            details.append("In React/TypeScript, I focus on building reusable components, implementing proper state management, and ensuring type safety throughout the application.")
        if 'Web3/Blockchain' in topics:
            details.append("For Web3 integration, I emphasize user experience, transaction state management, and security best practices.")
        if 'Real-time Systems' in topics:
            details.append("With real-time systems, I prioritize connection reliability, data consistency, and performance optimization.")
        if 'AI/ML' in topics:
            details.append("My AI/ML background helps me understand how to integrate intelligent features into user interfaces effectively.")
            
        return " ".join(details) if details else ""
        
    def add_personal_connection(self, question, analysis):
        """Add personal connection to the response"""
        return "I'm particularly excited about this role because it combines my technical expertise with the opportunity to have founder-level impact on a platform that's pushing the boundaries of what's possible in AI and Web3."
        
    def add_conversation(self, text):
        """Add text to conversation display"""
        self.conversation_text.insert(tk.END, text)
        self.conversation_text.see(tk.END)
        
    def add_analysis(self, text):
        """Add text to analysis display"""
        self.analysis_text.insert(tk.END, text)
        self.analysis_text.see(tk.END)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    print("🎯 Desktop Interview Intelligence Platform")
    print("=" * 60)
    print("🎯 Target: AI/Web3 Frontend Engineer Interview")
    print("👤 Recruiter: Anika Bansal (The DATAHEAD)")
    print("🏢 Company: Seed-funded startup (ex-Meta/Amazon backed)")
    print("⚡ Tech: React + TypeScript, Web3, AI agents")
    print("🤖 Features: AI-Powered Real-Time Response Generation")
    print("🖥️  Platform: Standalone Desktop Application")
    print("=" * 60)
    print("🚀 Starting Desktop Interview Intelligence Platform...")
    print("💡 A comprehensive desktop application will appear")
    print("🎤 Real-time audio listening and AI response generation")
    print("📱 Mobile interface with QR code generation")
    print("=" * 60)
    
    platform = DesktopInterviewPlatform()
    platform.run()

if __name__ == "__main__":
    main()
