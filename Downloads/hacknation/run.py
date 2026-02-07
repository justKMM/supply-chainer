"""
Launch script for the Ferrari Supply Chain Agents system.

Usage:
    python run.py

Opens the dashboard at http://localhost:8000
"""

import uvicorn
import webbrowser
import threading
import time


def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Ferrari Supply Chain Agents — One Click AI")
    print("  NANDA-Native Internet of Agents Simulation")
    print("=" * 60)
    print("\n  Starting server at http://localhost:8000")
    print("  Press Ctrl+C to stop\n")

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
