"""
Launch script for the Ferrari Supply Chain Agents system.

Usage:
    python run.py          # Backend only (use with Vite dev server)
    python run.py --build  # Build frontend and serve everything from :8000

Development workflow:
    Terminal 1: python run.py           → Backend API on http://localhost:8000
    Terminal 2: cd frontend && npm run dev → Frontend on http://localhost:5173

Production workflow:
    cd frontend && npm run build
    python run.py --build               → Everything on http://localhost:8000
"""

import uvicorn
import webbrowser
import threading
import time
import sys
import subprocess
from pathlib import Path


def open_browser(url: str):
    time.sleep(2)
    webbrowser.open(url)


if __name__ == "__main__":
    build_mode = "--build" in sys.argv
    frontend_dist = Path(__file__).parent / "frontend" / "dist"

    print("\n" + "=" * 60)
    print("  Ferrari Supply Chain Agents — One Click AI")
    print("  NANDA-Native Internet of Agents Simulation")
    print("=" * 60)

    if build_mode:
        print("\n  Building frontend...")
        subprocess.run(["npm", "run", "build"], cwd=str(Path(__file__).parent / "frontend"), check=True, shell=True)
        print("  Frontend built successfully.")
        url = "http://localhost:8000"
    elif frontend_dist.exists():
        url = "http://localhost:8000"
    else:
        url = "http://localhost:5173"

    print(f"\n  Backend API: http://localhost:8000")
    if url == "http://localhost:5173":
        print(f"  Frontend:    http://localhost:5173  (run 'cd frontend && npm run dev')")
    else:
        print(f"  Dashboard:   {url}")
    print("  Press Ctrl+C to stop\n")

    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
