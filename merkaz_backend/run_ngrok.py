import os
import sys
import shutil
import subprocess

#!/usr/bin/env python3
# File: run_ngrok.py
# Usage: python run_ngrok.py [PORT]
# Launches `ngrok http <PORT>`; on Windows opens a new console window.


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "8000"
    ngrok_path = shutil.which("ngrok")
    if not ngrok_path:
        print("Error: 'ngrok' not found in PATH. Install ngrok and add it to PATH.")
        sys.exit(1)

    cmd = [ngrok_path, "http", port]
    print("Running:", " ".join(cmd))

    if os.name == "nt":
        # On Windows, open ngrok in a new console window so you can interact with it separately.
        CREATE_NEW_CONSOLE = 0x00000010
        try:
            subprocess.Popen(cmd, creationflags=CREATE_NEW_CONSOLE)
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