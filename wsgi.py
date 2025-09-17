import os
os.environ.setdefault("CLOUD_DEPLOYMENT", "1")
from integrated_main_platform import IntegratedMainPlatform

platform = IntegratedMainPlatform()
app = platform.app

if __name__ == "__main__":
    # For local runs with gunicorn fallback
    platform.run()

