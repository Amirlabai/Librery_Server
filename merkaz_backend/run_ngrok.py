import os
import sys
import shutil
import subprocess
import time

#!/usr/bin/env python3
# File: run_ngrok.py
# Usage: python run_ngrok.py [BACKEND_PORT] [FRONTEND_PORT]
# Launches ngrok tunnels for both backend and frontend; on Windows opens new console windows.


def main():
    backend_port = sys.argv[1] if len(sys.argv) > 1 else "8000"
    frontend_port = sys.argv[2] if len(sys.argv) > 2 else "4200"
    
    ngrok_path = shutil.which("ngrok")
    if not ngrok_path:
        print("Error: 'ngrok' not found in PATH. Install ngrok and add it to PATH.")
        sys.exit(1)

    # Create ngrok configuration for multiple tunnels
    config_content = f"""version: "2"
authtoken_from_env: true
tunnels:
  backend:
    proto: http
    addr: {backend_port}
  frontend:
    proto: http
    addr: {frontend_port}
"""
    
    # Write config to temp file
    config_path = os.path.join(os.path.dirname(__file__), "ngrok.yml")
    with open(config_path, "w") as f:
        f.write(config_content)
    
    cmd = [ngrok_path, "start", "--config", config_path, "backend", "frontend"]
    print("Running:", " ".join(cmd))
    print(f"Backend tunnel: http://localhost:{backend_port} -> https://*.ngrok-free.app")
    print(f"Frontend tunnel: http://localhost:{frontend_port} -> https://*.ngrok-free.app")

    if os.name == "nt":
        # On Windows, open ngrok in a new console window so you can interact with it separately.
        CREATE_NEW_CONSOLE = 0x00000010
        try:
            subprocess.Popen(cmd, creationflags=CREATE_NEW_CONSOLE)
            print("ngrok started in new console window")
            print("Check the ngrok console for the public URLs")
        except OSError as e:
            print("Failed to start ngrok:", e)
            sys.exit(1)
    else:
        # On POSIX systems, attach output to this terminal.
        try:
            proc = subprocess.Popen(cmd)
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            proc.wait()

if __name__ == "__main__":
    main()