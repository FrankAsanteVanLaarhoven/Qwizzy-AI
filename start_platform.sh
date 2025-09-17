#!/bin/bash

# Interview Intelligence Platform Startup Script
# This script starts the integrated platform with microphone permission handling

echo "🎯 Starting Interview Intelligence Platform..."
echo "============================================================"
echo "🎯 Target: Academic/Research Interview with Bo WEI"
echo "👤 Recruiter: Bo WEI (Newcastle University)"
echo "🏢 Company: Newcastle University"
echo "⚡ Tech: AI/ML Research, Academic Collaboration"
echo "🤖 Features: AI-Powered Real-Time Response Generation"
echo "🌐 Platform: Web-Based Application with Microphone Support"
echo "============================================================"

# Navigate to the correct directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source interview_env/bin/activate

# Start the integrated platform
echo "🚀 Starting integrated platform on http://localhost:8000..."
echo "💡 The platform will open in your browser automatically"
echo "🎤 Make sure to grant microphone permissions when prompted"
echo "============================================================"

python integrated_main_platform.py
