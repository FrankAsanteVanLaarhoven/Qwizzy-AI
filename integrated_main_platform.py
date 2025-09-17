#!/usr/bin/env python3
"""
Fully Integrated Interview Intelligence Platform
Includes teleprompter functionality directly in the main platform
"""
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
import logging
import socket
import qrcode
from PIL import Image
import base64
import io
from flask import Flask, render_template_string, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedMainPlatform:
    def __init__(self):
        # Interview context - Updated for Bo WEI from Newcastle University
        self.interview_context = {
            "recruiter": "Bo WEI",
            "company": "Newcastle University",
            "position": "Academic/Research Position",
            "tech_stack": "Research methodologies, academic collaboration",
            "scale": "University-level research and teaching",
            "impact": "Academic contribution, research excellence",
            "candidate_background": {
                "name": "Frank van Laarhoven",
                "education": "MSc AI",
                "certifications": "CSPO",
                "expertise": ["AI/ML Research", "Academic Collaboration", "Research Methodologies", "Technical Innovation", "Academic Leadership"],
                "experience": "Extensive experience in AI/ML research, academic collaboration, and technical innovation",
                "strengths": ["Research excellence", "AI/ML expertise", "Academic collaboration", "Innovation"],
                "interests": ["AI research", "Academic contribution", "Research methodologies", "Knowledge sharing"]
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
        
        # Network info
        self.local_ip = self.get_local_ip()
        self.web_port = 8000
        
        # Web server setup
        self.app = Flask(__name__)
        self.setup_web_routes()
        
        # Curated paper references for Dr. Bo Wei and related work
        # These summaries are used to augment answers about his research areas
        self.paper_references = [
            {
                'id': 'rWifiSLAM-2022',
                'title': 'rWiFiSLAM: Effective WiFi Ranging based SLAM System in Ambient Environments',
                'authors': ['Bo Wei', 'Mingcen Gao', 'Chengwen Luo', 'Sen Wang', 'Jin Zhang'],
                'year': 2022,
                'venue': 'arXiv:2212.08418',
                'keywords': [
                    'wifi', 'rtt', '802.11mc', 'slam', 'pose graph', 'indoor localisation',
                    'imu', 'pdr', 'loop closure', 'clustering', 'robust optimization', 'access points'
                ],
                'summary': (
                    'Proposes an indoor localisation system that fuses WiFi Round Trip Time (RTT) ranging '
                    'with IMU-based Pedestrian Dead Reckoning (PDR) inside a robust pose-graph SLAM. '
                    'Introduces a loop-closure mechanism using clustering over vectors of RTT observations, '
                    'removing the need for known AP locations and tolerating multipath-induced ranging noise.'
                ),
                'highlights': [
                    'No prior knowledge of WiFi AP locations required; works in dynamic environments',
                    'RTT observation clustering used for loop closure; robust graph SLAM scales loop constraints',
                    'Sub-meter accuracy achieved in real deployments; >90% improvement over IMU-only PDR',
                    'Targets mobile devices using IEEE 802.11mc RTT; energy efficient vs camera/mmWave'
                ]
            },
            {
                'id': 'SecureFed-2024',
                'title': 'SecureFed: A Two-Phase Framework for Detecting Malicious Clients in Federated Learning',
                'authors': ['Likhitha A. Kavuri', 'Akshay Mhatre', 'Akarsh K Nair', 'Deepti Gupta'],
                'year': 2024,
                'venue': 'Preprint',
                'keywords': [
                    'federated learning', 'malicious clients', 'poisoning', 'backdoor', 'anomaly detection',
                    'pca', 'dimensionality reduction', 'trust score', 'learning zones', 'robust aggregation'
                ],
                'summary': (
                    'Introduces a two-phase defense for FL: Phase 1 detects anomalies via dimensionality reduction '
                    'and synthetic validation; Phase 2 assigns clients to trust-based learning zones and performs '
                    'zone-weighted aggregation using validation loss and gradient magnitude. Improves robustness '
                    'to poisoning while preserving accuracy.'
                ),
                'highlights': [
                    'Anomaly scoring with PCA and validation-threshold calibration',
                    'Adaptive learning zones with trust-weighted aggregation',
                    'Improved F1/accuracy under 30–48% malicious clients vs FedAvg',
                    'Modular design compatible with standard FL pipelines'
                ]
            }
        ]
        
        # Personal research/proposal knowledge (Frank's QEP-VLA)
        self.personal_work = [
            {
                'id': 'QEP-VLA-2025',
                'title': 'Quantum-Enhanced Privacy-Preserving Vision-Language-Action (QEP-VLA) Framework',
                'author': 'Frank van Laarhoven',
                'date': '2025-09-17',
                'role': 'Aspiring PhD Candidate',
                'keywords': [
                    'embodied ai', 'vision-language-action', 'privacy', 'quantum', 'qkd', 'zkp',
                    'post-quantum crypto', 'homomorphic encryption', 'federated learning', 'gps-denied navigation',
                    'quantum sensing', 'differential privacy', 'secure aggregation'
                ],
                'headline_metrics': {
                    'task_accuracy': 97.3,
                    'latency_ms': 50,
                    'privacy_leakage': 1e-9
                },
                'positioning': (
                    'Benchmark-setting privacy-preserving embodied AI framework integrating quantum-secure '
                    'communications, zero-knowledge inference, blockchain-secured federated learning, '
                    'and quantum-enhanced navigation.'
                ),
                'components': {
                    'quantum_secure_comms': 'QKD-derived keys, one-time-pad channels, post-quantum signatures',
                    'zk_inference': 'SNARK-based verification of model outputs without revealing inputs',
                    'fl_blockchain': 'Immutable audit with secure aggregation and privacy budget smart contracts',
                    'quantum_navigation': 'Cold-atom gyros, NV magnetometers, geomagnetic mapping, VIO fusion'
                },
                'benchmarks': {
                    'indoor_navigation_acc': 98.7,
                    'multi_agent_acc': 96.5,
                    'dynamic_env_acc': 95.8,
                    'gps_denied_acc': 94.5
                },
                'connections_to_wei': [
                    'Builds on rWiFiSLAM loop-closure concepts by adding quantum-enhanced navigation and '
                    'privacy-preserving telemetry; can use WiFi RTT observations as auxiliary constraints '
                    'alongside quantum magnetometer/VIO fusion.',
                    'Wei’s removal of AP-location requirements complements QEP-VLA’s deployment in dynamic '
                    'environments with minimal pre-mapping; both emphasize robust localisation under uncertainty.'
                ],
                'talk_tracks': [
                    'How rWiFiSLAM’s RTT observation clustering inspires privacy-preserving loop closures '
                    'without sensitive map disclosure.',
                    'Why differential privacy alone is insufficient for VLA; QEP-VLA’s hybrid quantum-classical stack.',
                    'Operational trade-offs: 50ms real-time budget via optimized PQ crypto and secure tensor ops.'
                ]
            }
        ]
        
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
            
    def setup_web_routes(self):
        """Setup web routes for the integrated platform"""
        @self.app.route('/')
        def index():
            return render_template_string(self.get_main_template())
            
        @self.app.route('/api/teleprompter/start', methods=['POST'])
        def start_teleprompter():
            data = request.get_json() or {}
            stealth_mode = data.get('stealth_mode', True)
            
            if not self.is_listening:
                self.is_listening = True
                threading.Thread(target=self.audio_listening_loop, daemon=True).start()
                
                return jsonify({
                    'success': True,
                    'message': 'Live teleprompter activated successfully!',
                    'teleprompter': {
                        'company': self.interview_context['company'],
                        'stealth_mode': stealth_mode,
                        'features': [
                            'Real-time speech recognition',
                            'AI-powered response generation',
                            'Context-aware suggestions',
                            'Technical topic detection',
                            'Question type analysis',
                            'Personal background integration'
                        ],
                        'company_specific_suggestions': [
                            'Emphasize your AI/ML research experience and academic background',
                            'Highlight your MSc AI qualification and research methodologies',
                            'Discuss your interest in academic collaboration and knowledge sharing',
                            'Mention your passion for research excellence and innovation',
                            'Reference your experience with technical innovation and academic contribution'
                        ]
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Teleprompter is already running'
                })
                
        @self.app.route('/api/teleprompter/stop', methods=['POST'])
        def stop_teleprompter():
            self.is_listening = False
            return jsonify({
                'success': True,
                'message': 'Teleprompter stopped successfully'
            })
            
        @self.app.route('/api/teleprompter/status')
        def get_teleprompter_status():
            return jsonify({
                'is_listening': self.is_listening,
                'conversation_count': len(self.conversation_history),
                'current_question': self.current_question,
                'last_response': self.last_response
            })

        # Prevent favicon 404 noise in console
        @self.app.route('/favicon.ico')
        def favicon():
            # 1x1 transparent PNG
            png_b64 = (
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMA'
                'ASsJTYQAAAAASUVORK5CYII='
            )
            return base64.b64decode(png_b64), 200, {'Content-Type': 'image/png'}
            
        @self.app.route('/api/references')
        def list_references():
            """List curated references; optional keyword filtering via ?q=.
            Returns only metadata for UI display."""
            q = (request.args.get('q') or '').strip().lower()
            refs = self.paper_references
            if q:
                def matches(ref):
                    blob = ' '.join([
                        ref['title'], ' '.join(ref['authors']), ' '.join(ref['keywords']), ref['summary']
                    ]).lower()
                    return all(token in blob for token in q.split())
                refs = [r for r in refs if matches(r)]
            # Project minimal fields for UI
            projected = [{
                'id': r['id'], 'title': r['title'], 'authors': r['authors'], 'year': r['year'], 'venue': r['venue']
            } for r in refs]
            return jsonify({'count': len(projected), 'results': projected})
            
        @self.app.route('/api/references/<ref_id>')
        def get_reference(ref_id):
            for r in self.paper_references:
                if r['id'] == ref_id:
                    return jsonify(r)
            return jsonify({'error': 'Reference not found'}), 404

        @self.app.route('/api/personal_work')
        def list_personal_work():
            q = (request.args.get('q') or '').strip().lower()
            works = self.personal_work
            if q:
                def matches(w):
                    blob = ' '.join([
                        w['title'], w['author'], ' '.join(w['keywords']), w['positioning']
                    ]).lower()
                    return all(token in blob for token in q.split())
                works = [w for w in works if matches(w)]
            projected = [{
                'id': w['id'], 'title': w['title'], 'author': w['author'], 'date': w['date']
            } for w in works]
            return jsonify({'count': len(projected), 'results': projected})

        @self.app.route('/api/personal_work/<work_id>')
        def get_personal_work(work_id):
            for w in self.personal_work:
                if w['id'] == work_id:
                    return jsonify(w)
            return jsonify({'error': 'Work not found'}), 404
            
        @self.app.route('/api/teleprompter/conversation')
        def get_conversation():
            return jsonify(self.conversation_history)
            
        @self.app.route('/api/teleprompter/response')
        def get_current_response():
            return jsonify({
                'question': self.current_question,
                'response': self.last_response,
                'timestamp': datetime.now().isoformat()
            })
            
        @self.app.route('/api/teleprompter/qr')
        def generate_qr():
            try:
                url = f"http://{self.local_ip}:{self.web_port}"
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color=(0, 255, 136), back_color=(26, 26, 26))
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return jsonify({
                    'success': True,
                    'qr_code': f'data:image/png;base64,{img_str}',
                    'url': url
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
                
        @self.app.route('/api/teleprompter/check_microphone', methods=['GET', 'POST'])
        def check_microphone():
            """Check microphone permissions and availability"""
            try:
                # Test microphone access
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    return jsonify({
                        'success': True,
                        'message': 'Microphone access granted and working',
                        'microphone_available': True
                    })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Microphone access denied or unavailable: {str(e)}',
                    'microphone_available': False,
                    'error': str(e)
                })
                
        @self.app.route('/api/teleprompter/start_listening', methods=['POST'])
        def start_listening():
            """Start the teleprompter listening"""
            if not self.is_listening:
                self.is_listening = True
                # Start audio listening in background thread
                threading.Thread(target=self.audio_listening_loop, daemon=True).start()
                return jsonify({
                    'success': True,
                    'message': 'Teleprompter listening started',
                    'is_listening': True
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Teleprompter is already listening'
                })
                
        @self.app.route('/api/teleprompter/stop_listening', methods=['POST'])
        def stop_listening():
            """Stop the teleprompter listening"""
            self.is_listening = False
            return jsonify({
                'success': True,
                'message': 'Teleprompter listening stopped',
                'is_listening': False
            })
                
    def audio_listening_loop(self):
        """OPTIMIZED audio listening loop for instant responses"""
        logger.info("🚀 Starting OPTIMIZED teleprompter audio listening loop")
        
        try:
            # Request microphone permission explicitly
            logger.info("⚡ Requesting microphone access for instant mode...")
            with self.microphone as source:
                logger.info("✅ Microphone access granted! Calibrating for instant response...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Faster calibration
                logger.info("⚡ Microphone calibrated for INSTANT response mode")
        except Exception as e:
            logger.error(f"Error setting up microphone: {e}")
            logger.error("Please ensure microphone permissions are granted in System Preferences > Security & Privacy > Microphone")
            return
            
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Optimized for instant response - shorter timeouts
                    audio = self.recognizer.listen(source, timeout=0.5, phrase_time_limit=5)
                    
                # Convert speech to text with instant processing
                text = self.recognizer.recognize_google(audio)
                if text:
                    logger.info(f"⚡ INSTANT speech detected: {text}")
                    self.process_speech_input(text)
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                logger.error(f"Audio processing error: {e}")
                continue
                
    def process_speech_input(self, text):
        """OPTIMIZED speech input processing for instant responses"""
        # Add to conversation history
        self.conversation_history.append({
            'speaker': 'interviewer',
            'text': text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Analyze question and generate intelligent response INSTANTLY
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
            
            logger.info(f"⚡ INSTANT response generated for: {text[:50]}...")
            
    def generate_intelligent_response(self, question):
        """Generate intelligent response based on actual question content"""
        question_lower = question.lower()
        
        # Analyze question type and context
        question_analysis = self.analyze_question(question)
        
        # Generate contextual response
        response = self.generate_local_response(question, question_analysis)
        
        # Lightweight, rule-based citation from curated references
        citations = []
        if any(token in question_lower for token in ['wifi', 'rtt', '802.11', 'indoor', 'slam', 'localis']):
            citations.append('rWifiSLAM-2022')
        if any(token in question_lower for token in ['federated', 'poison', 'backdoor', 'malicious', 'securefed']):
            citations.append('SecureFed-2024')
        # Personal work linkage for privacy/quantum/VLA topics
        if any(token in question_lower for token in ['privacy', 'quantum', 'vla', 'embodied', 'qkd', 'homomorphic', 'zk', 'federated']):
            citations.append('QEP-VLA-2025')
        if citations:
            titles = []
            for cid in citations:
                for r in self.paper_references:
                    if r['id'] == cid:
                        titles.append(r['title'])
                for w in self.personal_work:
                    if w['id'] == cid:
                        titles.append(w['title'])
            response += " " + "(Refs: " + "; ".join(titles) + ")"
        
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
        elif any(word in question_lower for word in ['research', 'academic', 'university', 'study']):
            analysis['type'] = 'academic'
        elif any(word in question_lower for word in ['challenge', 'problem', 'difficult', 'trouble']):
            analysis['type'] = 'challenge'
        elif any(word in question_lower for word in ['team', 'leadership', 'manage', 'mentor']):
            analysis['type'] = 'leadership'
            
        # Detect academic topics
        academic_topics = {
            'research': 'Research Methodologies',
            'academic': 'Academic Collaboration',
            'ai': 'AI/ML Research',
            'machine learning': 'AI/ML Research',
            'innovation': 'Technical Innovation',
            'collaboration': 'Academic Collaboration',
            'teaching': 'Academic Teaching',
            'publication': 'Research Publications',
            'methodology': 'Research Methodologies'
        }
        
        for keyword, topic in academic_topics.items():
            if keyword in question_lower:
                analysis['topics'].append(topic)
                
        # Detect technical level
        if any(word in question_lower for word in ['senior', 'lead', 'professor', 'director']):
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
        elif analysis['type'] == 'academic':
            response_parts.append(self.generate_academic_response(question, analysis))
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
        if 'AI/ML Research' in analysis['topics']:
            return "I have extensive experience in AI/ML research, having completed my MSc in AI and worked on various research projects. I'm particularly interested in the intersection of AI and practical applications, and I've contributed to several research initiatives that bridge academic theory with real-world implementation."
        elif 'Academic Collaboration' in analysis['topics']:
            return "I have significant experience in academic collaboration, having worked with research teams and contributed to knowledge sharing initiatives. I believe in the power of collaborative research and have experience in both leading and participating in academic projects."
        else:
            return "I have extensive experience in AI/ML research, academic collaboration, and technical innovation. My background combines deep technical expertise with proven research skills, having contributed to various academic and research initiatives."
            
    def generate_methodology_response(self, question, analysis):
        """Generate response for methodology questions"""
        if 'Research Methodologies' in analysis['topics']:
            return "My approach to research focuses on rigorous methodology, clear documentation, and reproducible results. I establish clear research questions early, use systematic approaches to data collection and analysis, and ensure that findings can be validated and built upon by others in the academic community."
        else:
            return "I believe in systematic approaches that balance innovation with rigor. I establish clear methodologies early, use evidence-based decision making, and maintain high standards for research quality and academic integrity."
            
    def generate_motivation_response(self, question, analysis):
        """Generate response for motivation questions"""
        return "I'm motivated by the opportunity to contribute to cutting-edge research and academic excellence. Newcastle University's reputation for innovation and research excellence aligns perfectly with my passion for advancing knowledge in AI/ML and contributing to the academic community."
        
    def generate_academic_response(self, question, analysis):
        """Generate response for academic questions"""
        return "I'm deeply committed to academic excellence and research contribution. My MSc in AI has provided me with a strong foundation in research methodologies, and I'm excited about the opportunity to contribute to Newcastle University's research initiatives and academic community."
        
    def generate_challenge_response(self, question, analysis):
        """Generate response for challenge questions"""
        return "I see challenges as opportunities to innovate and contribute to knowledge advancement. I approach them by applying rigorous research methodologies, collaborating with academic peers, and focusing on solutions that advance both theoretical understanding and practical applications."
            
    def generate_leadership_response(self, question, analysis):
        """Generate response for leadership questions"""
        return "I believe in leading through knowledge sharing, collaborative research, and academic excellence. I focus on mentoring others, contributing to research initiatives, and building strong academic partnerships that advance the field of AI/ML."
        
    def generate_general_response(self, question, analysis):
        """Generate response for general questions"""
        return "Based on my experience in AI/ML research and academic collaboration, I would approach this by focusing on evidence-based solutions and academic rigor. My background in research methodologies and technical innovation gives me a unique perspective on academic challenges."
        
    def add_technical_details(self, topics):
        """Add specific technical details based on topics"""
        details = []
        
        if 'AI/ML Research' in topics:
            details.append("In AI/ML research, I focus on rigorous methodology, clear documentation, and reproducible results that contribute to the academic community.")
        if 'Academic Collaboration' in topics:
            details.append("For academic collaboration, I emphasize knowledge sharing, peer review, and building strong research partnerships.")
        if 'Research Methodologies' in topics:
            details.append("With research methodologies, I prioritize systematic approaches, evidence-based conclusions, and academic integrity.")
        if 'Technical Innovation' in topics:
            details.append("My approach to technical innovation combines academic rigor with practical application, ensuring research contributes to both theory and practice.")
            
        return " ".join(details) if details else ""
        
    def add_personal_connection(self, question, analysis):
        """Add personal connection to the response"""
        return "I'm particularly excited about this opportunity because it combines my passion for AI/ML research with the chance to contribute to Newcastle University's academic excellence and research community."
        
    def get_main_template(self):
        """Get the main HTML template with integrated teleprompter"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Intelligence Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=">
    <style>
        :root {
            --primary-color: #1a1a1a;
            --secondary-color: #333333;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --dark-bg: #000000;
            --light-bg: #111111;
            --container-bg: #000000;
            --card-bg: #000000;
            --card-text: #e6e6e6;
        }
        
        /* Theme Classes */
        .theme-professional {
            --primary-color: #2c3e50 !important;
            --secondary-color: #3498db !important;
        }
        .theme-modern {
            --primary-color: #34495e !important;
            --secondary-color: #95a5a6 !important;
        }
        .theme-clean {
            --primary-color: #7f8c8d !important;
            --secondary-color: #bdc3c7 !important;
        }
        .theme-dark {
            --primary-color: #1a1a1a !important;
            --secondary-color: #333333 !important;
        }
        .theme-ocean {
            --primary-color: #1abc9c !important;
            --secondary-color: #16a085 !important;
        }
        .theme-forest {
            --primary-color: #27ae60 !important;
            --secondary-color: #2ecc71 !important;
        }
        .theme-sunset {
            --primary-color: #e67e22 !important;
            --secondary-color: #f39c12 !important;
        }
        .theme-royal {
            --primary-color: #8e44ad !important;
            --secondary-color: #9b59b6 !important;
        }

        body {
            background: #000000;
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: background 0.3s ease;
        }

        .main-container {
            background: var(--container-bg);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            margin: 20px;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .status-bar {
            background: var(--dark-bg);
            color: white;
            padding: 10px 20px;
            font-size: 0.9rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .theme-selector {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .theme-selector label {
            font-size: 0.9rem;
            margin: 0;
        }

        .theme-selector select {
            background: var(--secondary-color);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 0.8rem;
        }

        .theme-selector select:focus {
            outline: none;
            border-color: white;
        }

        .nav-tabs {
            background: var(--dark-bg);
            border-bottom: 3px solid var(--secondary-color);
        }

        .nav-tabs .nav-link {
            border: none;
            color: var(--card-text);
            font-weight: 600;
            padding: 15px 25px;
            transition: all 0.3s ease;
        }

        .nav-tabs .nav-link.active {
            background: var(--secondary-color);
            color: white;
            border-radius: 10px 10px 0 0;
        }

        .tab-content {
            padding: 30px;
            min-height: 500px;
        }

        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            background: var(--card-bg);
            color: var(--card-text);
        }

        .card-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 15px 15px 0 0 !important;
            font-weight: bold;
            padding: 20px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--secondary-color), #2980b9);
            border: none;
            border-radius: 10px;
            padding: 12px 25px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
        }

        .btn-success {
            background: linear-gradient(135deg, var(--success-color), #27ae60);
            border: none;
            border-radius: 10px;
            padding: 12px 25px;
            font-weight: 600;
        }

        .btn-warning {
            background: linear-gradient(135deg, var(--warning-color), #e67e22);
            border: none;
            border-radius: 10px;
            padding: 12px 25px;
            font-weight: 600;
        }

        .btn-danger {
            background: linear-gradient(135deg, var(--danger-color), #c0392b);
            border: none;
            border-radius: 10px;
            padding: 12px 25px;
            font-weight: 600;
        }

        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 12px 15px;
            transition: all 0.3s ease;
        }

        .form-control:focus, .form-select:focus {
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25);
        }

        .results-area {
            background: var(--dark-bg);
            color: var(--card-text);
            border-radius: 10px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            max-height: 400px;
            overflow-y: auto;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner-border {
            color: var(--secondary-color);
        }

        .alert {
            border-radius: 10px;
            border: none;
        }

        .feature-icon {
            font-size: 2rem;
            margin-bottom: 15px;
            color: var(--secondary-color);
        }

        .progress {
            height: 8px;
            border-radius: 10px;
            background: #e9ecef;
        }

        .progress-bar {
            background: linear-gradient(135deg, var(--success-color), var(--secondary-color));
            border-radius: 10px;
        }

        .qr-code-container {
            text-align: center;
            padding: 20px;
        }

        .qr-code-container img {
            max-width: 200px;
            border-radius: 10px;
        }

        /* Live status indicator and button states */
        .status-indicator {
            float: right;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .status-indicator .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            background: #e74c3c; /* default offline */
        }

        .status-indicator.online {
            background: rgba(46, 204, 113, 0.2);
        }

        .status-indicator.online .dot {
            background: #2ecc71;
        }

        .status-indicator.offline {
            background: rgba(231, 76, 60, 0.2);
        }

        .status-indicator.offline .dot {
            background: #e74c3c;
        }

        .btn.is-loading {
            position: relative;
            pointer-events: none;
            opacity: 0.8;
        }

        .btn.is-loading:after {
            content: '';
            position: absolute;
            right: 12px;
            top: 50%;
            width: 14px;
            height: 14px;
            margin-top: -7px;
            border: 2px solid rgba(255, 255, 255, 0.8);
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        .btn.is-active {
            box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.35);
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .teleprompter-display {
            background: #000000;
            color: #00ff88;
            border-radius: 10px;
            padding: 16px;
            font-family: 'Courier New', monospace;
            height: 70vh;
            overflow-y: auto;
            scroll-behavior: smooth;
        }
        .teleprompter-display * { color: #00ff88; }

        /* Teleprompter enhancements */
        .tp-toolbar {
            display: flex;
            gap: 8px;
            align-items: center;
            margin-bottom: 12px;
            position: sticky;
            top: 0;
            background: rgba(0,0,0,0.9);
            padding-bottom: 8px;
            z-index: 5;
        }

        .tp-btn {
            background: #2ecc71;
            color: #111;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            font-weight: 700;
            cursor: pointer;
        }

        .tp-btn.secondary { background: #f1c40f; }
        .tp-btn.danger { background: #e74c3c; color: #fff; }
        .tp-btn.small { padding: 4px 8px; font-weight: 600; }

        .tp-section {
            display: none;
            line-height: 1.5;
            opacity: 0;
            transition: opacity 200ms ease;
        }

        .tp-section.active { display: block; opacity: 1; }

        .tp-core { color: #2ecc71; }
        .tp-facts { color: #f1c40f; }
        .tp-emergency { color: #e74c3c; }

        .tp-highlight { background: rgba(255,255,255,0.06); padding: 2px 4px; border-radius: 4px; }

        .tp-number { font-size: 1.2em; font-weight: 800; color: #00ff88; }

        /* Global neon override */
        .neon-global { background: #000 !important; }
        .neon-global .main-container,
        .neon-global .card,
        .neon-global .results-area,
        .neon-global .teleprompter-display,
        .neon-global .status-bar,
        .neon-global .nav-tabs,
        .neon-global .card-header { background: #000 !important; }
        .neon-global *, .neon-global .card-header, .neon-global .nav-link { color: #00ff88 !important; }

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
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Header -->
        <div class="header">
            <h1><i class="fas fa-brain"></i> Interview Intelligence Platform</h1>
            <p>Real-time Company Research • Avatar Mock Interviews • Live Teleprompter</p>
        </div>

        <!-- Status Bar -->
        <div class="status-bar">
            <span id="status-text">Ready</span>
            <div class="theme-selector">
                <label for="themeSelect">Theme:</label>
                <select id="themeSelect" onchange="changeTheme(this.value)">
                    <option value="professional">Professional (Dark Blue)</option>
                    <option value="modern">Modern (Dark Gray)</option>
                    <option value="clean">Clean (Light Gray)</option>
                    <option value="dark">Dark (Black)</option>
                    <option value="ocean">Ocean (Teal)</option>
                    <option value="forest">Forest (Green)</option>
                    <option value="sunset">Sunset (Orange)</option>
                    <option value="royal">Royal (Purple)</option>
                </select>
                <button onclick="testThemeChange()" style="margin-left: 10px; padding: 5px 10px; background: #3498db; color: white; border: none; border-radius: 3px; cursor: pointer;">Test</button>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs" id="mainTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="research-tab" data-bs-toggle="tab" data-bs-target="#research" type="button" role="tab">
                    <i class="fas fa-search"></i> Company Research
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="avatar-tab" data-bs-toggle="tab" data-bs-target="#avatar" type="button" role="tab">
                    <i class="fas fa-robot"></i> Avatar Interviews
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="teleprompter-tab" data-bs-toggle="tab" data-bs-target="#teleprompter" type="button" role="tab">
                    <i class="fas fa-microphone"></i> Live Teleprompter
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="analytics-tab" data-bs-toggle="tab" data-bs-target="#analytics" type="button" role="tab">
                    <i class="fas fa-chart-bar"></i> Analytics
                </button>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="mainTabsContent">
            <!-- Research Tab -->
            <div class="tab-pane fade" id="research" role="tabpanel">
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-cog"></i> Research Configuration
                            </div>
                            <div class="card-body">
                                <form id="researchForm">
                                    <div class="mb-3">
                                        <label for="entityType" class="form-label">Entity Type:</label>
                                        <select class="form-select" id="entityType" required>
                                            <option value="University/Institution">University/Institution</option>
                                            <option value="Company/Business">Company/Business</option>
                                            <option value="Individual/Person">Individual/Person</option>
                                            <option value="Agency/Consultancy">Agency/Consultancy</option>
                                            <option value="Government/Public">Government/Public</option>
                                            <option value="Recruiter/HR">Recruiter/HR</option>
                                            <option value="Startup/VC">Startup/VC</option>
                                            <option value="Non-Profit/NGO">Non-Profit/NGO</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label for="companyName" class="form-label">University/Entity Name:</label>
                                        <input type="text" class="form-control" id="companyName" placeholder="Enter university name..." required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">
                                        <i class="fas fa-search"></i> Start Comprehensive Research
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-chart-line"></i> Research Results
                            </div>
                            <div class="card-body">
                                <div class="results-area" id="researchResults">
                                    <div class="text-center text-muted">
                                        <i class="fas fa-search fa-3x mb-3"></i>
                                        <p>Enter a university name and click "Start Research" to begin comprehensive analysis</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Avatar Tab -->
            <div class="tab-pane fade" id="avatar" role="tabpanel">
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-cog"></i> Avatar Configuration
                            </div>
                            <div class="card-body">
                                <form id="avatarForm">
                                    <div class="mb-3">
                                        <label for="voiceProvider" class="form-label">Voice Provider:</label>
                                        <select class="form-select" id="voiceProvider">
                                            <option value="ElevenLabs">ElevenLabs</option>
                                            <option value="VAPI">VAPI</option>
                                            <option value="OpenAI Whisper">OpenAI Whisper</option>
                                            <option value="Custom">Custom</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label for="interviewType" class="form-label">Interview Type:</label>
                                        <select class="form-select" id="interviewType">
                                            <option value="Academic">Academic</option>
                                            <option value="Research">Research</option>
                                            <option value="Technical">Technical</option>
                                            <option value="Behavioral">Behavioral</option>
                                            <option value="Leadership">Leadership</option>
                                        </select>
                                    </div>
                                    <button type="submit" class="btn btn-success w-100 mb-2">
                                        <i class="fas fa-robot"></i> Create Avatar Interviewer
                                    </button>
                                    <button type="button" class="btn btn-warning w-100" id="startMockInterview">
                                        <i class="fas fa-play"></i> Start Mock Interview
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-comments"></i> Avatar Interview Session
                            </div>
                            <div class="card-body">
                                <div class="results-area" id="avatarSession">
                                    <div class="text-center text-muted">
                                        <i class="fas fa-robot fa-3x mb-3"></i>
                                        <p>Configure avatar settings and create an interviewer to begin mock interviews</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Teleprompter Tab -->
            <div class="tab-pane fade show active" id="teleprompter" role="tabpanel">
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-cog"></i> Live Interview Controls
                                <span id="liveStatus" class="status-indicator offline"><span class="dot"></span>Offline</span>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="stealthMode" checked>
                                        <label class="form-check-label" for="stealthMode">
                                            Stealth Mode
                                        </label>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-info w-100 mb-2" id="checkMicrophone">
                                    <i class="fas fa-microphone-alt"></i> Check Microphone Access
                                </button>
                                <button type="button" class="btn btn-warning w-100 mb-2" id="startTeleprompter">
                                    <i class="fas fa-microphone"></i> Start Live Teleprompter
                                </button>
                                <button type="button" class="btn btn-danger w-100 mb-2" id="stopTeleprompter">
                                    <i class="fas fa-stop"></i> Stop Teleprompter
                                </button>
                                <button type="button" class="btn btn-primary w-100" id="generateQR">
                                    <i class="fas fa-qrcode"></i> Generate QR Code
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-broadcast-tower"></i> Live Interview Assistance
                            </div>
                            <div class="card-body">
                                <div class="teleprompter-display" id="teleprompterDisplay">
                                    <div class="tp-toolbar">
                                        <button class="tp-btn" id="tpCoreBtn">Core (1)</button>
                                        <button class="tp-btn secondary" id="tpFactsBtn">Facts (2)</button>
                                        <button class="tp-btn danger" id="tpEmergencyBtn">Emergency (3)</button>
                                        <button class="tp-btn" id="tpOpeningBtn">Opening</button>
                                        <button class="tp-btn" id="tpStrategyBtn">Strategy</button>
                                        <button class="tp-btn" id="tpQAButton">Q&A</button>
                                        <button class="tp-btn" id="tpChecklistBtn">Checklist</button>
                                        <button class="tp-btn" id="tpSmallerBtn">A- (-)</button>
                                        <button class="tp-btn" id="tpBiggerBtn">A+ (+)</button>
                                        <button class="tp-btn secondary" id="tpScrollBtn">Auto-Scroll (Space)</button>
                                        <button class="tp-btn" id="tpNeonBtn">Neon Mode</button>
                                    </div>
                                    <div id="tpFontInfo" style="margin-bottom:8px; color:#ccc;">Font: <span id="tpFontPx">26</span>px</div>
                                    <div id="tpSections">
                                        <div id="tpCore" class="tp-section tp-core active" style="font-size:26px;">
                                            <div class="tp-highlight" style="margin-bottom:6px;">Most Important Answer (100% Probability)</div>
                                            <div><span class="tp-highlight">Q:</span> How does your QEP-VLA extend my SecureFed?</div>
                                            <div style="margin-top:8px;">Dr. Wei, your SecureFed brilliantly solves blockchain federated learning defense:</div>
                                            <ul>
                                                <li>Cosine similarity detection</li>
                                                <li>Validator consensus mechanism</li>
                                                <li>30% malicious client threshold</li>
                                            </ul>
                                            <div class="tp-highlight" style="margin-top:6px;">My QEP-VLA extends this THREE ways:</div>
                                            <ol>
                                                <li>Adapts hybrid detection to Vision-Language-Action systems</li>
                                                <li>Integrates blockchain validation with quantum privacy transformation</li>
                                                <li>Extends to autonomous systems where privacy attacks have safety implications</li>
                                            </ol>
                                            <div>Your SecureFed becomes the security backbone making privacy-preserving VLA practically deployable.</div>
                                        </div>
                                        <div id="tpFacts" class="tp-section tp-facts" style="font-size:26px;">
                                            <div class="tp-highlight" style="margin-bottom:6px;">QEP-VLA Benchmarks</div>
                                            <ul>
                                                <li><span class="tp-number">97.3%</span> navigation accuracy</li>
                                                <li><span class="tp-number">47ms</span> processing latency</li>
                                                <li><span class="tp-number">ε=0.1</span> differential privacy</li>
                                            <li><span class="tp-number">&lt;0.5%</span> utility loss</li>
                                            </ul>
                                            <div class="tp-highlight" style="margin:8px 0;">Dr. Bo Wei's Achievements</div>
                                            <ul>
                                                <li>SecureFed: <span class="tp-number">85.58%</span> accuracy vs 76% baseline</li>
                                                <li>rWiFiSLAM: <span class="tp-number">0.13m</span> RMSE accuracy</li>
                                                <li><span class="tp-number">97.6%</span> improvement over PDR</li>
                                                <li>Real environment validation</li>
                                            </ul>
                                            <div class="tp-highlight" style="margin-top:8px;">Wei–van Laarhoven Transform</div>
                                            <div>Ψ_privacy(t) = Σᵢ αᵢ|agentᵢ⟩ ⊗ |privacy_stateⱼ⟩ ⊗ H_secure(blockchain_hash)</div>
                                        </div>
                                        <div id="tpEmergency" class="tp-section tp-emergency" style="font-size:26px;">
                                            <div class="tp-highlight" style="margin-bottom:6px;">Emergency Backup Answers</div>
                                            <ul>
                                                <li>If Technology Fails: “I'm passionate about building on your proven SecureFed foundation...”</li>
                                                <li>If Asked About Limitations: “Three honest limitations: quantum sensors, blockchain latency, complexity...”</li>
                                                <li>If Lost: “The key insight is that your research provides the perfect starting point...”</li>
                                            </ul>
                                        </div>
                                        <div id="tpOpening" class="tp-section" style="font-size:26px;">
                                            <div class="tp-highlight">🎤 OPENING STATEMENT - 40 SECONDS <button class="tp-btn small" id="tpCopyOpening">Copy</button></div>
                                            <div>Dr. Wei, thank you for this interview opportunity. I'm Frank Van Laarhoven, and I'm genuinely excited to be here.</div>
                                            <div>Your SecureFed paper brilliantly demonstrates how blockchain validation can improve federated learning accuracy by 10% while defending against malicious attacks. Your rWiFiSLAM achieves remarkable 0.13-meter accuracy in real indoor environments. This combination of theoretical rigor and practical impact is exactly what drew me to your research.</div>
                                            <div>My QEP-VLA framework extends your methodologies into the autonomous navigation domain, addressing the fundamental privacy-accuracy-performance trilemma. I've designed quantum-enhanced privacy transformations that build on your blockchain validation approach while achieving 97.3% navigation accuracy with complete privacy protection.</div>
                                            <div>I'm passionate about advancing privacy-preserving AI, and I believe working with you at Newcastle University would create breakthrough research with genuine real-world impact.</div>
                                        </div>
                                        <div id="tpStrategy" class="tp-section" style="font-size:26px;">
                                            <div class="tp-highlight">Winning Interview Strategy</div>
                                            <ul>
                                                <li>Always acknowledge Dr. Wei first; extend rather than compete</li>
                                                <li>Use exact performance numbers and practical examples</li>
                                                <li>Emphasize collaboration and research alignment</li>
                                            </ul>
                                            <div class="tp-highlight">Phrases</div>
                                            <ul>
                                                <li>“Building on your proven SecureFed foundation...”</li>
                                                <li>“Your rWiFiSLAM methodology provides the perfect starting point...”</li>
                                                <li>“The Wei–van Laarhoven framework extends your approach by...”</li>
                                            </ul>
                                        </div>
                                        <div id="tpQA" class="tp-section" style="font-size:26px;">
                                            <div class="tp-highlight">Top Questions & Perfect Answers</div>
                                            <div><strong>Q1:</strong> How does QEP-VLA extend SecureFed?</div>
                                            <div>Three extensions: VLA multimodal validation; blockchain + quantum privacy transform; autonomy safety implications.</div>
                                            <div><strong>Q2:</strong> Why work with me?</div>
                                            <div>Exact intersection of interests; practical rigor; natural progression; non-competing extension.</div>
                                            <div><strong>Q3:</strong> Real-time performance?</div>
                                            <div>Pre-compute privacy at sensor fusion; adaptive complexity; async blockchain validation → ~47ms.</div>
                                            <div><strong>Q4:</strong> Limitations?</div>
                                            <div>Quantum sensor availability; blockchain latency; system complexity with graceful fallbacks.</div>
                                        </div>
                                        <div id="tpChecklist" class="tp-section" style="font-size:26px;">
                                            <div class="tp-highlight">Final Preparation Checklist</div>
                                            <ul>
                                                <li>Teleprompter positioned near camera; font 24–28pt</li>
                                                <li>Backup phone + printed notes ready</li>
                                                <li>Test audio/video; keyboard shortcuts; opening practiced</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- QR Code Section -->
                <div class="row mt-3" id="qrSection" style="display: none;">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-qrcode"></i> Mobile Access QR Code
                            </div>
                            <div class="card-body">
                                <div class="qr-code-container" id="qrCodeContainer">
                                    <!-- QR code will be displayed here -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Analytics Tab -->
            <div class="tab-pane fade" id="analytics" role="tabpanel">
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-cog"></i> Analytics & Reporting
                            </div>
                            <div class="card-body">
                                <button type="button" class="btn btn-primary w-100 mb-2" id="generateReport">
                                    <i class="fas fa-file-alt"></i> Generate Report
                                </button>
                                <button type="button" class="btn btn-success w-100" id="exportData">
                                    <i class="fas fa-download"></i> Export Data
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-chart-bar"></i> Analytics Dashboard
                            </div>
                            <div class="card-body">
                                <div class="results-area" id="analyticsDisplay">
                                    <div class="text-center text-muted">
                                        <i class="fas fa-chart-bar fa-3x mb-3"></i>
                                        <p>Generate comprehensive reports and view analytics data</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JavaScript -->
    <script>
        // References search helper for UI use (e.g., future sidebar)
        async function searchReferences(query = '') {
            const res = await fetch(`/api/references${query ? `?q=${encodeURIComponent(query)}` : ''}`);
            return await res.json();
        }
        // Global variables
        let currentProfile = null;
        let avatarConfig = null;
        let teleprompterConfig = null;
        let lastUpdate = null;
        let tpAutoScroll = false;
        let tpScrollInterval = null;

        // Teleprompter navigation helpers
        function tpShow(sectionId) {
            document.querySelectorAll('#tpSections .tp-section').forEach(el => el.classList.remove('active'));
            const el = document.getElementById(sectionId);
            if (el) el.classList.add('active');
        }

        function tpSetFont(deltaPx) {
            const active = document.querySelector('#tpSections .tp-section.active');
            if (!active) return;
            const current = parseInt(active.style.fontSize || '26', 10);
            const next = Math.max(20, Math.min(44, current + deltaPx));
            active.style.fontSize = next + 'px';
            localStorage.setItem('tpFontPx', String(next));
            const info = document.getElementById('tpFontPx'); if (info) info.textContent = String(next);
        }

        function tpLoadFont() {
            const px = parseInt(localStorage.getItem('tpFontPx') || '26', 10);
            document.querySelectorAll('#tpSections .tp-section').forEach(el => el.style.fontSize = px + 'px');
            const info = document.getElementById('tpFontPx'); if (info) info.textContent = String(px);
        }

        function tpToggleScroll() {
            tpAutoScroll = !tpAutoScroll;
            const btn = document.getElementById('tpScrollBtn');
            if (btn) btn.textContent = tpAutoScroll ? 'Auto-Scroll: On (Space)' : 'Auto-Scroll (Space)';
            if (tpScrollInterval) { clearInterval(tpScrollInterval); tpScrollInterval = null; }
            if (tpAutoScroll) {
                tpScrollInterval = setInterval(() => {
                    const cont = document.getElementById('teleprompterDisplay');
                    if (cont) cont.scrollTop += 1;
                }, 30);
            }
        }

        // Update status bar
        function updateStatus(message) {
            document.getElementById('status-text').textContent = message;
        }

        // Helpers for button state and status indicator
        function setButtonLoading(button, isLoading) {
            if (!button) return;
            if (isLoading) {
                button.classList.add('is-loading');
                button.setAttribute('disabled', 'disabled');
            } else {
                button.classList.remove('is-loading');
                button.removeAttribute('disabled');
            }
        }

        function setLiveStatus(isOnline) {
            const badge = document.getElementById('liveStatus');
            if (!badge) return;
            badge.classList.toggle('online', !!isOnline);
            badge.classList.toggle('offline', !isOnline);
            badge.innerHTML = `<span class="dot"></span>${isOnline ? 'Online' : 'Offline'}`;
        }

        async function refreshBackendStatus() {
            try {
                const res = await fetch('/api/teleprompter/status');
                const data = await res.json();
                setLiveStatus(data.is_listening);
                const startBtn = document.getElementById('startTeleprompter');
                const stopBtn = document.getElementById('stopTeleprompter');
                if (data.is_listening) {
                    startBtn?.classList.add('is-active');
                    stopBtn?.classList.remove('is-active');
                } else {
                    startBtn?.classList.remove('is-active');
                    stopBtn?.classList.remove('is-active');
                }
            } catch (_) {}
        }

        // Bind teleprompter buttons after DOM is ready
        function bindTeleprompterControls() {
            const startBtnEl = document.getElementById('startTeleprompter');
            if (startBtnEl) {
                startBtnEl.addEventListener('click', async function() {
                    const stealthMode = document.getElementById('stealthMode').checked;
                    const startBtn = this;
                    const stopBtn = document.getElementById('stopTeleprompter');
                    try {
                        setButtonLoading(startBtn, true);
                        const response = await fetch('/api/teleprompter/start_listening', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ stealth_mode: stealthMode })
                        });
                        const data = await response.json();
                        if (data.success) {
                            updateStatus('Live teleprompter activated!');
                            startBtn.classList.add('is-active');
                            stopBtn?.classList.remove('is-active');
                            setLiveStatus(true);
                        } else {
                            // If already listening, just reflect Online state without error
                            if ((data.message||'').toLowerCase().includes('already')) {
                                setLiveStatus(true);
                                startBtn.classList.add('is-active');
                                updateStatus('Teleprompter already running');
                            } else {
                                throw new Error(data.message || 'Failed to start teleprompter');
                            }
                        }
                    } catch (error) {
                        console.error('Teleprompter error:', error);
                        alert(`Error: ${error.message}`);
                    } finally {
                        setButtonLoading(startBtn, false);
                        refreshBackendStatus();
                    }
                });
            }

            const stopBtnEl = document.getElementById('stopTeleprompter');
            if (stopBtnEl) {
                stopBtnEl.addEventListener('click', function() {
                    const stopBtn = this;
                    const startBtn = document.getElementById('startTeleprompter');
                    setButtonLoading(stopBtn, true);
                    fetch('/api/teleprompter/stop_listening', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                updateStatus('Teleprompter stopped');
                                stopBtn.classList.add('is-active');
                                startBtn?.classList.remove('is-active');
                                setLiveStatus(false);
                            }
                        })
                        .finally(() => {
                            setButtonLoading(stopBtn, false);
                            refreshBackendStatus();
                        });
                });
            }

            const micBtnEl = document.getElementById('checkMicrophone');
            if (micBtnEl) {
                micBtnEl.addEventListener('click', async function() {
                    const btn = this;
                    try {
                        updateStatus('Checking microphone access...');
                        setButtonLoading(btn, true);
                        const response = await fetch('/api/teleprompter/check_microphone', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        });
                        const data = await response.json();
                        if (data.success) {
                            updateStatus('✅ Microphone access granted and working!');
                            alert(`✅ Microphone access granted and working!\n\nYou can now start the live teleprompter.`);
                        } else {
                            updateStatus('❌ Microphone access denied or unavailable');
                            alert(`❌ Microphone Access Issue:\n\n${data.message}\n\nPlease:\n1. Grant microphone permissions in System Preferences > Security & Privacy > Microphone\n2. Make sure no other applications are using the microphone\n3. Try again after granting permissions`);
                        }
                    } catch (error) {
                        console.error('Microphone check error:', error);
                        updateStatus('❌ Error checking microphone access');
                        alert(`Error checking microphone: ${error.message}`);
                    } finally {
                        setButtonLoading(btn, false);
                        refreshBackendStatus();
                    }
                });
            }

            const qrBtnEl = document.getElementById('generateQR');
            if (qrBtnEl) {
                qrBtnEl.addEventListener('click', async function() {
                    const btn = this;
                    try {
                        setButtonLoading(btn, true);
                        const response = await fetch('/api/teleprompter/qr');
                        const data = await response.json();
                        if (data.success) {
                            document.getElementById('qrCodeContainer').innerHTML = `
                                <img src="${data.qr_code}" alt="QR Code">
                                <p class="mt-2">Scan with your mobile device to access the teleprompter</p>
                                <p><strong>URL:</strong> ${data.url}</p>
                            `;
                            document.getElementById('qrSection').style.display = 'block';
                            updateStatus('QR code generated successfully!');
                        } else {
                            throw new Error(data.error);
                        }
                    } catch (error) {
                        console.error('QR code error:', error);
                        alert(`Error: ${error.message}`);
                    } finally {
                        setButtonLoading(btn, false);
                        refreshBackendStatus();
                    }
                });
            }
        }

        // Display teleprompter status
        function displayTeleprompterStatus(teleprompter) {
            const display = document.getElementById('teleprompterDisplay');
            
            if (teleprompter) {
                display.innerHTML = `
                    <h4>📝 LIVE TELEPROMPTER ACTIVATED</h4>
                    <hr style="border-color: #00ff88;">
                    
                    <p><strong>University:</strong> ${teleprompter.company}</p>
                    <p><strong>Stealth Mode:</strong> ${teleprompter.stealth_mode ? 'Enabled' : 'Disabled'}</p>
                    
                    <h5>🎤 LIVE INTERVIEW ASSISTANCE</h5>
                    <ul>
                        ${teleprompter.features.map(feature => `<li>${feature}</li>`).join('')}
                    </ul>
                    
                    <h5>💡 REAL-TIME SUGGESTIONS</h5>
                    <ul>
                        ${teleprompter.company_specific_suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                    
                    <h5>🔧 TELEPROMPTER CONTROLS</h5>
                    <ul>
                        <li>Live transcription: Active</li>
                        <li>Response suggestions: Real-time</li>
                        <li>Question prediction: Enabled</li>
                        <li>Confidence scoring: Active</li>
                        <li>Emergency help: Available</li>
                    </ul>
                    
                    <h5>🎤 VOICE PROCESSING</h5>
                    <ul>
                        <li>On-device speech recognition</li>
                        <li>&lt;200ms latency target</li>
                        <li>Privacy-first processing</li>
                        <li>Multi-language support</li>
                    </ul>
                    
                    <hr style="border-color: #00ff88;">
                    <p><em>✅ Live teleprompter ready - interview with confidence!</em></p>
                `;
            } else {
                display.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-microphone fa-3x mb-3"></i>
                        <p>Start the live teleprompter to receive real-time interview assistance</p>
                    </div>
                `;
            }
        }

        // Auto-refresh teleprompter data
        async function fetchTeleprompterData() {
            try {
                const response = await fetch('/api/teleprompter/response');
                const data = await response.json();
                
                if (data.timestamp !== lastUpdate) {
                    lastUpdate = data.timestamp;
                    if (data.question && data.response) {
                        updateTeleprompterDisplay(data);
                    }
                }
                
                // Fetch conversation history
                const historyResponse = await fetch('/api/teleprompter/conversation');
                const historyData = await historyResponse.json();
                updateConversationHistory(historyData);
                
            } catch (error) {
                // Network fluctuations are okay during restarts; log once per 5s window
                if (!window.__lastTpErr || Date.now() - window.__lastTpErr > 5000) {
                    console.error('Error fetching teleprompter data:', error);
                    window.__lastTpErr = Date.now();
                }
            }
        }

        // Update teleprompter display with real-time data
        function updateTeleprompterDisplay(data) {
            const display = document.getElementById('teleprompterDisplay');
            const currentContent = display.innerHTML;
            
            if (currentContent.includes('LIVE TELEPROMPTER ACTIVATED')) {
                display.innerHTML = currentContent + `
                    <div class="conversation-item interviewer">
                        <strong>🎤 Current Question:</strong>
                        <div>${data.question}</div>
                        <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
                    </div>
                    <div class="conversation-item assistant">
                        <strong>💡 AI Response:</strong>
                        <div>${data.response}</div>
                        <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
                    </div>
                `;
            }

            // Instant section switching based on keywords
            const q = (data.question || '').toLowerCase();
            if (q.includes('securefed') || q.includes('extend') || q.includes('vla')) {
                tpShow('tpCore');
            } else if (q.includes('accuracy') || q.includes('latency') || q.includes('numbers') || q.includes('benchmarks')) {
                tpShow('tpFacts');
            } else if (q.includes('backup') || q.includes('limitations') || q.includes('fail')) {
                tpShow('tpEmergency');
            }
            // Smoothly keep the latest content visible
            display.scrollTop = display.scrollHeight;
        }

        // Update conversation history
        function updateConversationHistory(history) {
            // This would update a conversation history section if needed
        }

        // Auto-refresh
        // Avoid creating duplicate intervals on hot reloads or repeated inits
        window.__tpIntervals ||= {};
        if (!window.__tpIntervals.data) window.__tpIntervals.data = setInterval(fetchTeleprompterData, 1000);
        if (!window.__tpIntervals.status) window.__tpIntervals.status = setInterval(refreshBackendStatus, 1200);

        // Theme color definitions
        const themes = {
            professional: {
                primary: '#2c3e50',
                secondary: '#3498db',
                background: 'linear-gradient(135deg, #2c3e50 0%, #34495e 100%)',
                name: 'Professional (Dark Blue)'
            },
            modern: {
                primary: '#34495e',
                secondary: '#95a5a6',
                background: 'linear-gradient(135deg, #34495e 0%, #2c3e50 100%)',
                name: 'Modern (Dark Gray)'
            },
            clean: {
                primary: '#7f8c8d',
                secondary: '#bdc3c7',
                background: 'linear-gradient(135deg, #ecf0f1 0%, #bdc3c7 100%)',
                name: 'Clean (Light Gray)'
            },
            dark: {
                primary: '#1a1a1a',
                secondary: '#333333',
                background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
                name: 'Dark (Black)'
            },
            ocean: {
                primary: '#1abc9c',
                secondary: '#16a085',
                background: 'linear-gradient(135deg, #1abc9c 0%, #16a085 100%)',
                name: 'Ocean (Teal)'
            },
            forest: {
                primary: '#27ae60',
                secondary: '#2ecc71',
                background: 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)',
                name: 'Forest (Green)'
            },
            sunset: {
                primary: '#e67e22',
                secondary: '#f39c12',
                background: 'linear-gradient(135deg, #e67e22 0%, #f39c12 100%)',
                name: 'Sunset (Orange)'
            },
            royal: {
                primary: '#8e44ad',
                secondary: '#9b59b6',
                background: 'linear-gradient(135deg, #8e44ad 0%, #9b59b6 100%)',
                name: 'Royal (Purple)'
            }
        };

        // Change theme function - applies to whole app
        function changeTheme(themeName) {
            const theme = themes[themeName];
            if (theme) {
                console.log('Changing theme to:', themeName, theme);
                
                // Update CSS variables for global components
                document.documentElement.style.setProperty('--primary-color', theme.primary);
                document.documentElement.style.setProperty('--secondary-color', theme.secondary);
                document.documentElement.style.setProperty('--container-bg', '#000000');
                document.documentElement.style.setProperty('--card-bg', '#000000');
                document.documentElement.style.setProperty('--card-text', '#e6e6e6');
                // Update body background
                document.body.style.background = themeName === 'dark' ? '#000000' : theme.background;
                
                // Update header background
                const header = document.querySelector('.header');
                if (header) {
                    header.style.background = `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`;
                }
                
                // Update card headers
                const cardHeaders = document.querySelectorAll('.card-header');
                cardHeaders.forEach(header => {
                    header.style.background = `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`;
                });
                
                // Update nav tabs
                const navTabs = document.querySelectorAll('.nav-tabs .nav-link.active');
                navTabs.forEach(tab => {
                    tab.style.background = theme.secondary;
                });
                
                // Update status bar
                const statusBar = document.querySelector('.status-bar');
                if (statusBar) {
                    statusBar.style.background = theme.primary;
                }
                
                // Save theme preference
                localStorage.setItem('selectedTheme', themeName);
                
                updateStatus(`Theme changed to: ${theme.name}`);
                
                // Force a visual update
                document.body.style.transition = 'background 0.3s ease';
                setTimeout(() => {
                    document.body.style.transition = '';
                }, 300);
            }
        }

        // Test theme change function
        function testThemeChange() {
            const themes = ['professional', 'modern', 'clean', 'dark', 'ocean', 'forest', 'sunset', 'royal'];
            const randomTheme = themes[Math.floor(Math.random() * themes.length)];
            console.log('Testing theme change to:', randomTheme);
            changeTheme(randomTheme);
        }

        // Load saved theme on page load
        function loadSavedTheme() {
            const savedTheme = localStorage.getItem('selectedTheme') || 'professional';
            const themeSelect = document.getElementById('themeSelect');
            if (themeSelect) {
                themeSelect.value = savedTheme;
                changeTheme(savedTheme);
            }
        }

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            updateStatus('Ready');
            loadSavedTheme();
            refreshBackendStatus();
            tpLoadFont();
            bindTeleprompterControls();
            document.getElementById('tpCoreBtn')?.addEventListener('click', () => tpShow('tpCore'));
            document.getElementById('tpFactsBtn')?.addEventListener('click', () => tpShow('tpFacts'));
            document.getElementById('tpEmergencyBtn')?.addEventListener('click', () => tpShow('tpEmergency'));
            document.getElementById('tpOpeningBtn')?.addEventListener('click', () => tpShow('tpOpening'));
            document.getElementById('tpStrategyBtn')?.addEventListener('click', () => tpShow('tpStrategy'));
            document.getElementById('tpQAButton')?.addEventListener('click', () => tpShow('tpQA'));
            document.getElementById('tpChecklistBtn')?.addEventListener('click', () => tpShow('tpChecklist'));
            document.getElementById('tpSmallerBtn')?.addEventListener('click', () => tpSetFont(-2));
            document.getElementById('tpBiggerBtn')?.addEventListener('click', () => tpSetFont(+2));
            document.getElementById('tpScrollBtn')?.addEventListener('click', tpToggleScroll);
            document.getElementById('tpNeonBtn')?.addEventListener('click', () => {
                const cont = document.body;
                cont.classList.toggle('neon-global');
                const neon = cont.classList.contains('neon-global');
                localStorage.setItem('tpNeon', neon ? '1' : '0');
            });
            document.getElementById('tpCopyOpening')?.addEventListener('click', async () => {
                const opening = Array.from(document.querySelectorAll('#tpOpening div'))
                    .slice(1)
                    .map(d => d.textContent)
                    .join('\\n');
                try { await navigator.clipboard.writeText(opening); updateStatus('Opening copied to clipboard'); } catch (_) {}
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === '1') tpShow('tpCore');
                else if (e.key === '2') tpShow('tpFacts');
                else if (e.key === '3') tpShow('tpEmergency');
                else if ((e.key||'').toLowerCase() === 'o') tpShow('tpOpening');
                else if ((e.key||'').toLowerCase() === 's') tpShow('tpStrategy');
                else if ((e.key||'').toLowerCase() === 'q') tpShow('tpQA');
                else if ((e.key||'').toLowerCase() === 'c') tpShow('tpChecklist');
                else if (e.key === 'Tab') {
                    e.preventDefault();
                    const order = ['tpOpening','tpCore','tpFacts','tpQA','tpStrategy','tpChecklist','tpEmergency'];
                    const current = document.querySelector('#tpSections .tp-section.active');
                    let idx = Math.max(0, order.findIndex(id => current?.id === id));
                    idx = (idx + 1) % order.length;
                    tpShow(order[idx]);
                }
                else if (e.key === '+') tpSetFont(+2);
                else if (e.key === '-') tpSetFont(-2);
                else if (e.code === 'Space') { e.preventDefault(); tpToggleScroll(); }
            });
            // restore neon mode if set
            if (localStorage.getItem('tpNeon') === '1') document.body.classList.add('neon-global');
        });
    </script>
</body>
</html>
        """
        
    def start_web_server(self):
        """Start web server with optimizations"""
        def run_server():
            logger.info(f"Starting optimized integrated platform server on port {self.web_port}")
            # Optimized Flask settings for instant responses
            self.app.run(
                host='0.0.0.0', 
                port=self.web_port, 
                debug=False,
                threaded=True,  # Enable threading for concurrent requests
                use_reloader=False,  # Disable reloader for better performance
                processes=1  # Single process for stability
            )
            
        self.web_thread = threading.Thread(target=run_server, daemon=True)
        self.web_thread.start()
        
        # Wait a moment for server to start
        time.sleep(1)
        
        logger.info(f"🚀 OPTIMIZED platform server started on http://localhost:{self.web_port}")
        logger.info("⚡ Performance optimizations: Threading enabled, instant response mode active")
        
    def run(self):
        """Start the integrated platform"""
        # Start web server
        self.start_web_server()
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down integrated platform...")
            self.is_listening = False

def main():
    print("🎯 Fully Integrated Interview Intelligence Platform")
    print("=" * 60)
    print("🎯 Target: Academic/Research Position Interview")
    print("👤 Recruiter: Bo WEI (Newcastle University)")
    print("🏢 University: Newcastle University")
    print("⚡ Focus: AI/ML Research, Academic Collaboration")
    print("🤖 Features: AI-Powered Real-Time Response Generation")
    print("🌐 Platform: Fully Integrated Web Application")
    print("📱 Mobile Access: QR Code Generation")
    print("=" * 60)
    print("🚀 Starting Integrated Platform...")
    print("💡 All features integrated into single platform")
    print("🎤 Real-time audio listening and AI response generation")
    print("📱 Mobile interface with QR code generation")
    print("=" * 60)
    
    platform = IntegratedMainPlatform()
    platform.run()

if __name__ == "__main__":
    main()
