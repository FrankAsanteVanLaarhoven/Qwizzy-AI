# 🎯 Interview Intelligence Platform

A comprehensive AI-powered interview assistance system with advanced microphone permission handling and stealth teleprompter capabilities, designed specifically for your interview with Bo WEI from Newcastle University.

## 🚀 Quick Start

### Option 1: Easy Startup Script (RECOMMENDED)
```bash
cd /Users/frankvanlaarhoven/Desktop/InterviewIntelligencePlatform
./start_platform.sh
```

### Option 2: Manual Startup
```bash
cd /Users/frankvanlaarhoven/Desktop/InterviewIntelligencePlatform
source interview_env/bin/activate
python integrated_main_platform.py
```

### Access the Platform
- **Desktop**: http://localhost:8000 (opens automatically)
- **Mobile**: Scan QR code generated in the platform
- **Network**: http://[YOUR_IP]:8000 for other devices

## 🎯 Current Interview Context

**Target Role:** Academic/Research Position  
**Recruiter:** Bo WEI (Newcastle University)  
**Company:** Newcastle University  
**Tech Stack:** AI/ML Research, Academic Collaboration, Research Methodologies  
**Focus:** Research excellence, academic contribution, knowledge sharing  
**Scale:** University-level research and teaching  
**Impact:** Academic contribution, research excellence  

## 🎤 Microphone Permission Setup

The platform now includes comprehensive microphone permission handling:

1. **Click "Check Microphone Access"** first in the Live Teleprompter tab
2. **Grant permissions** when macOS prompts you
3. **Verify access** with the built-in test
4. **Start Live Teleprompter** once permissions are confirmed

### Troubleshooting Microphone Issues:
- Go to **System Preferences > Security & Privacy > Microphone**
- Ensure **Python** or **Terminal** has microphone access
- Close other applications that might be using the microphone
- Restart the platform if needed

## 🎮 How to Use

### **Pre-Interview Setup:**
1. ✅ Run the platform: `./start_platform.sh` or `python integrated_main_platform.py`
2. 🎤 Check microphone access: Click "Check Microphone Access"
3. 🎤 Test audio listening: Click "Start Live Teleprompter" and speak
4. 📱 Generate QR code: Click "Generate QR Code" for mobile access
5. 📱 Test mobile interface: Scan QR code and verify access

### **During Interview:**
1. 🎤 Start stealth teleprompter before the interview begins
2. 📱 Use mobile interface for discreet access to AI responses
3. 💡 Follow AI suggestions for intelligent, contextual academic answers
4. 📝 Monitor conversation on desktop for full context

## 🤖 AI Features

- **Real-time Audio Processing** - Listens to interview questions
- **Intelligent Response Generation** - Context-aware academic responses
- **Research Topic Detection** - AI/ML, academic collaboration, research methodologies
- **Question Type Analysis** - Experience, research impact, teaching, motivation
- **Academic Background Integration** - MSc AI, research experience, academic interests
- **Stealth Mode** - Operates invisibly in the background
- **Mobile QR Access** - Easy mobile device setup

## 🎯 Stealth Teleprompter Capabilities

- **Background Audio Listening**: Continuously monitors conversation
- **Real-time Speech Recognition**: Converts speech to text instantly
- **Intelligent Question Analysis**: Detects academic/research topics
- **Context-aware Response Generation**: Provides relevant answers for Bo WEI interview
- **Stealth Mode**: Operates invisibly in the background
- **Mobile QR Access**: Generate QR code for mobile device access
- **Academic Context**: Tailored responses for university research positions

## 📱 Mobile Access

- **QR Code Generation** - One-click mobile setup
- **Responsive Interface** - Works on any device
- **Real-time Updates** - Live conversation monitoring
- **Discreet Access** - Professional appearance
- **Academic Focus** - Tailored for university interviews

## 🔧 Technical Details

- **Integrated Platform** - Single Flask application with teleprompter built-in
- **Microphone Permission Handling** - Explicit permission requests and testing
- **Flask Backend** - RESTful API for real-time communication
- **Speech Recognition** - Google Speech-to-Text integration
- **Cross-Platform** - Works on Mac, Windows, Linux
- **Stealth Operation** - Background processing with invisible operation

## 📁 File Structure

```
InterviewIntelligencePlatform/
├── integrated_main_platform.py    # Main integrated platform (RECOMMENDED)
├── start_platform.sh             # Easy startup script
├── web_interview_platform.py     # Alternative platform version
├── requirements.txt              # Python dependencies
├── interview_env/                # Virtual environment
├── templates/                    # HTML templates
│   ├── interview_platform.html   # Main platform interface
│   └── teleprompter.html         # Mobile teleprompter interface
├── static/                       # CSS, JS, and assets
└── README.md                     # This file
```

## 🎓 Academic Interview Tips

- **Research Excellence**: Emphasize your MSc AI background
- **Collaboration**: Highlight academic collaboration experience
- **Innovation**: Discuss technical innovation and research methodologies
- **Teaching**: Mention interest in knowledge sharing and mentoring
- **University Values**: Align with Newcastle University's mission

## 🔧 Troubleshooting

### Microphone Issues
- **Permission Denied**: Check System Preferences > Security & Privacy > Microphone
- **No Audio**: Ensure no other apps are using the microphone
- **Poor Recognition**: Speak clearly and reduce background noise

### Platform Issues
- **Port Conflicts**: Platform uses port 8000 by default
- **Virtual Environment**: Always activate with `source interview_env/bin/activate`
- **Mobile Access**: Ensure both devices are on the same network

### Academic Interview Specific
- **Research Context**: Platform is pre-configured for Bo WEI interview
- **University Focus**: Responses tailored for Newcastle University
- **Academic Topics**: Optimized for research and collaboration questions

## 🎯 Ready for Your Interview!

Your Interview Intelligence Platform is now organized and ready to help you ace your interview with Bo WEI from Newcastle University. The AI will provide intelligent, contextual responses based on the actual questions being asked, helping you showcase your expertise in AI/ML research, academic collaboration, and technical innovation.

**Good luck with your interview!** 🚀✨