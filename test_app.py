#!/usr/bin/env python3
"""
Minimal test app for Render deployment debugging
"""
import os
from flask import Flask, jsonify

# Set cloud deployment flag
os.environ.setdefault("CLOUD_DEPLOYMENT", "1")

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'ok',
        'message': 'Test app is running',
        'cloud': os.getenv('CLOUD_DEPLOYMENT', '0') == '1'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'cloud': os.getenv('CLOUD_DEPLOYMENT', '0') == '1'
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
