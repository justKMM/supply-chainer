"""
Launch script for the Ferrari Supply Chain Agents system.

Usage:
    python run.py

Starts the backend API at http://localhost:8000
Starts the React UI dev server at http://localhost:5173
"""

import os
import subprocess
import sys
import threading
import time
import webbrowser
import uvicorn
from dotenv import load_dotenv

load_dotenv()

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:5173")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Ferrari Supply Chain Agents — One Click AI")
    print("  NANDA-Native Internet of Agents Simulation")
    print("=" * 60)
    print("\n  Starting API server at http://localhost:8000")
    print("  Starting React UI at http://localhost:5173")
    print("  Press Ctrl+C to stop\n")

    threading.Thread(target=open_browser, daemon=True).start()

    npm_cmd = "npm.cmd" if sys.platform.startswith("win") else "npm"
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    frontend_process = subprocess.Popen([npm_cmd, "run", "dev"], cwd=frontend_dir)

    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )
    finally:
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
