import os
import sys
import shutil
import subprocess
import time
import json
import urllib.request
import threading

#!/usr/bin/env python3
# File: run_ngrok.py
# Usage: python run_ngrok.py [PORT]
# Launches ngrok tunnel for Flask server (serves both frontend and backend on single port).


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "8000"
    
    ngrok_path = shutil.which("ngrok")
    if not ngrok_path:
        print("=" * 70)
        print("ERROR: 'ngrok' not found in PATH.")
        print("=" * 70)
        print("\nTo install ngrok on Windows:")
        print("\nOption 1 - Using winget (Windows Package Manager):")
        print("  winget install ngrok.ngrok")
        print("\nOption 2 - Using Chocolatey:")
        print("  choco install ngrok")
        print("\nOption 3 - Manual installation:")
        print("  1. Visit: https://dashboard.ngrok.com/get-started/setup")
        print("  2. Download ngrok for Windows")
        print("  3. Extract ngrok.exe to a folder (e.g., C:\\ngrok)")
        print("  4. Add that folder to your system PATH:")
        print("     - Press Win+X and select 'System'")
        print("     - Click 'Advanced system settings'")
        print("     - Click 'Environment Variables'")
        print("     - Under 'System variables', find 'Path' and click 'Edit'")
        print("     - Click 'New' and add the folder path (e.g., C:\\ngrok)")
        print("     - Click 'OK' on all dialogs")
        print("  5. Restart your terminal/PowerShell")
        print("\nAfter installation, verify with: ngrok version")
        print("=" * 70)
        sys.exit(1)
    
    # Find ngrok.yml config file (one level up from dev_toolkit directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), "ngrok.yml")
    
    def fetch_tunnel_urls():
        """Fetch tunnel URLs from ngrok API after a short delay."""
        time.sleep(3)  # Wait for ngrok to start
        try:
            # ngrok API is typically at http://127.0.0.1:4040/api/tunnels
            with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels") as response:
                data = json.loads(response.read())
                tunnels = data.get("tunnels", [])
                
                print("\n" + "=" * 70)
                print("NGROK TUNNEL URL:")
                print("=" * 70)
                
                app_url = None
                
                for tunnel in tunnels:
                    name = tunnel.get("name", "")
                    public_url = tunnel.get("public_url", "")
                    config = tunnel.get("config", {})
                    addr = config.get("addr", "")
                    
                    if "app" in name.lower() or port in addr or "8000" in addr:
                        app_url = public_url
                        print(f"Application (port {port}): {public_url}")
                    else:
                        print(f"{name}: {public_url}")
                
                if app_url:
                    print("\n" + "=" * 70)
                    print("SETUP INSTRUCTIONS:")
                    print("=" * 70)
                    print("1. Access your application at:", app_url)
                    print("2. Flask serves both frontend and backend on the same port")
                    print("3. API calls use relative URLs (same origin) - no configuration needed!")
                    print("=" * 70)
                else:
                    print("\n⚠️  Warning: Could not fetch tunnel URL. Check ngrok console.")
                    
        except Exception as e:
            print(f"\n⚠️  Could not fetch tunnel URLs automatically: {e}")
            print("\nYou can also check the ngrok web interface at: http://127.0.0.1:4040")
            print("Or check the ngrok console window for the URL.")
    
    cmd = [ngrok_path, "start", "--config", config_path, "app"]
    print("Running:", " ".join(cmd))
    print(f"Application tunnel: http://localhost:{port} -> https://*.ngrok-free.app")
    print(f"Note: Flask serves both frontend (Angular build) and backend (API) on port {port}")
    
    # Start a thread to fetch URLs after ngrok starts
    url_thread = threading.Thread(target=fetch_tunnel_urls, daemon=True)

    if os.name == "nt":
        # On Windows, open ngrok in a new console window so you can interact with it separately.
        CREATE_NEW_CONSOLE = 0x00000010
        try:
            subprocess.Popen(cmd, creationflags=CREATE_NEW_CONSOLE)
            print("ngrok started in new console window")
            url_thread.start()
            print("Fetching tunnel URLs...")
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