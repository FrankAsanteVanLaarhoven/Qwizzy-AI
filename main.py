import os
import uvicorn


def run() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port_str = os.getenv("PORT", "8000")
    reload_enabled = os.getenv("RELOAD", "true").lower() == "true"
    uvicorn.run("web_app:app", host=host, port=int(port_str), reload=reload_enabled)


if __name__ == "__main__":
    run()


