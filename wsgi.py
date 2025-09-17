import os
os.environ.setdefault("CLOUD_DEPLOYMENT", "1")
from integrated_main_platform import IntegratedMainPlatform

# Render-specific environment setup
if not os.getenv('PORT'):
    os.environ['PORT'] = '10000'  # Render default port

platform = IntegratedMainPlatform()
app = platform.app

if __name__ == "__main__":
    # For local runs with gunicorn fallback
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

