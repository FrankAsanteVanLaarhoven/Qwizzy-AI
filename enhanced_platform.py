#!/usr/bin/env python3
"""
Enhanced Interview Intelligence Platform with Integrated Teleprompter
"""
import subprocess
import time
import webbrowser
import os
import sys
import threading
from pathlib import Path

def start_teleprompter_server():
    """Start the teleprompter server in a separate thread"""
    try:
        subprocess.run([sys.executable, "teleprompter_server.py"], check=True)
    except Exception as e:
        print(f"Error starting teleprompter server: {e}")

def main():
    print("🎯 Enhanced Interview Intelligence Platform")
    print("=" * 60)
    print("🌐 Main Platform: http://localhost:8000")
    print("🤖 AI Teleprompter: http://localhost:8081")
    print("📱 Mobile Interface: QR code available in teleprompter")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("teleprompter_server.py"):
        print("❌ Error: teleprompter_server.py not found")
        print("Please run this script from the InterviewIntelligencePlatform directory")
        return
    
    try:
        # Start the teleprompter server in a separate thread
        print("🚀 Starting AI Teleprompter Server on port 8081...")
        teleprompter_thread = threading.Thread(target=start_teleprompter_server, daemon=True)
        teleprompter_thread.start()
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Open the main platform
        print("🌐 Opening main Interview Intelligence Platform...")
        webbrowser.open("http://localhost:8000")
        
        # Wait a moment then open the teleprompter
        time.sleep(2)
        print("🤖 Opening AI Teleprompter interface...")
        webbrowser.open("http://localhost:8081")
        
        print("\n✅ Enhanced Platform Started Successfully!")
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
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down enhanced platform...")
            print("✅ Platform stopped successfully")
            
    except Exception as e:
        print(f"❌ Error starting platform: {e}")
        return

if __name__ == "__main__":
    main()
