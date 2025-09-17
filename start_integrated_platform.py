#!/usr/bin/env python3
"""
Start Integrated Interview Intelligence Platform
Combines the main platform (port 8000) with the AI teleprompter (port 8081)
"""
import subprocess
import time
import webbrowser
import os
import sys
from pathlib import Path

def main():
    print("🎯 Starting Integrated Interview Intelligence Platform")
    print("=" * 60)
    print("🌐 Main Platform: http://localhost:8000")
    print("🤖 AI Teleprompter: http://localhost:8081")
    print("📱 Mobile Interface: QR code available in teleprompter")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("integrated_teleprompter.py"):
        print("❌ Error: integrated_teleprompter.py not found")
        print("Please run this script from the InterviewIntelligencePlatform directory")
        return
    
    try:
        # Start the integrated teleprompter
        print("🚀 Starting AI Teleprompter on port 8081...")
        teleprompter_process = subprocess.Popen([
            sys.executable, "integrated_teleprompter.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the teleprompter to start
        time.sleep(3)
        
        # Open the main platform
        print("🌐 Opening main Interview Intelligence Platform...")
        webbrowser.open("http://localhost:8000")
        
        # Wait a moment then open the teleprompter
        time.sleep(2)
        print("🤖 Opening AI Teleprompter interface...")
        webbrowser.open("http://localhost:8081")
        
        print("\n✅ Integrated Platform Started Successfully!")
        print("=" * 60)
        print("📋 Instructions:")
        print("1. Use the main platform (port 8000) for company research")
        print("2. Use the teleprompter (port 8081) for live interview assistance")
        print("3. Click 'Generate QR Code' in teleprompter for mobile access")
        print("4. Start audio listening before your interview begins")
        print("=" * 60)
        print("Press Ctrl+C to stop the platform")
        
        # Keep the script running
        try:
            teleprompter_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down integrated platform...")
            teleprompter_process.terminate()
            teleprompter_process.wait()
            print("✅ Platform stopped successfully")
            
    except Exception as e:
        print(f"❌ Error starting platform: {e}")
        return

if __name__ == "__main__":
    main()
