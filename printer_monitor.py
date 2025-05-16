# printer_monitor.py
import time
import socket
import os
import getpass
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import toml  # Requires Python 3.11+ or install via pip install toml for older versions
from pythonEmailNotify import EmailSender

print("Printer monitor starting!", flush=True)

# ==== PATH CONFIG ====
LOG_FILE = Path("/home/sovol/printer_data/logs/klippy.log")
CONFIG_FILE = Path("/home/sovol/printer_monitor/printer_monitor_config.toml")
EVENT_LOG_FILE = Path("/home/sovol/printer_monitor/monitor_events.log")

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.expanduser("~/printer_monitor/printer_monitor.env"))

# Email sender setup
emailer = EmailSender(
    smtp_server="smtp.gmail.com",
    port=587,
    login=os.environ["SMTP_EMAIL"],
    password=os.environ["SMTP_PASS"],
    default_recipient=os.environ["SMTP_TO"]
)

# Get system info
USER = getpass.getuser()
HOSTNAME = socket.gethostname()
DEVICE_NAME = f"{USER}@{HOSTNAME}"

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "Unavailable"

LOCAL_IP = get_local_ip()

# Load TOML config
config = toml.load(CONFIG_FILE)

def current_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(tag: str, message: str):
    with EVENT_LOG_FILE.open("a") as f:
        f.write(f"[{current_time_str()}] [{tag}] {message}\n")

def monitor_klipper_log():
    print("Printer monitor starting!")

    paused_sent = False
    complete_sent = False

    try:
        with LOG_FILE.open("r") as log:
            log.seek(0, 2)  # Go to end of file

            while True:
                line = log.readline()
                if not line:
                    time.sleep(0.5)
                    continue

                line_lower = line.lower()

                # === Detect Print Complete ===
                if any(kw.lower() in line_lower for kw in config['complete']['keywords']) and not complete_sent:
                    if config['complete']['notify']:
                        subject = "✅ Klipper Print Finished"
                        body = f"""Your printer has completed a print.

Device: {DEVICE_NAME}
IP: {LOCAL_IP}
Time: {current_time_str()}

Log line:
{line.strip()}
"""
                        print(f"[DEBUG] Sending email: {subject}", flush=True)
                        emailer.sendEmail(subject, body)
                    if config['complete']['log']:
                        log_event("COMPLETE", line.strip())
                    paused_sent = False
                    return

                # === Detect Pause ===
                elif any(kw.lower() in line_lower for kw in config['pause']['keywords']) and not paused_sent:
                    reason = "Unknown"
                    if "runout" in line_lower:
                        reason = "Filament runout detected"
                    elif "action: pause" in line_lower:
                        reason = "Klipper pause command"

                    if config['pause']['notify']:
                        subject = "🛑 Klipper Print Paused"
                        body = f"""Your printer has paused.

Device: {DEVICE_NAME}
IP: {LOCAL_IP}
Time: {current_time_str()}

Likely reason: {reason}

Log line:
{line.strip()}
"""
                        print(f"[DEBUG] Sending email: {subject}", flush=True)
                        emailer.sendEmail(subject, body)
                    if config['pause']['log']:
                        log_event("PAUSE", line.strip())
                    paused_sent = True
                    complete_sent = False

                # === Reset Pause State if Print Resumed ===
                elif any(kw.lower() in line_lower for kw in config['resume']['keywords']):
                    if config['resume']['log']:
                        log_event("RESUME", line.strip())
                    paused_sent = False

                # === Detect Shutdown/Error ===
                elif any(kw.lower() in line_lower for kw in config['error']['keywords']):
                    if config['error']['notify'] or config['error']['log']:
                        print("[❌] Shutdown detected — waiting 5 seconds to collect related log lines...")
                        shutdown_lines = [line.strip()]

                        end_time = time.time() + 5
                        while time.time() < end_time:
                            next_line = log.readline()
                            if not next_line:
                                time.sleep(0.1)
                                continue
                            if "shutdown" in next_line.lower():
                                shutdown_lines.append(next_line.strip())

                        if config['error']['notify']:
                            subject = "❌ Klipper Print Failed"
                            body = f"""Your printer has stopped due to an error.

Device: {DEVICE_NAME}
IP: {LOCAL_IP}
Time: {current_time_str()}

Collected log lines:
{chr(10).join(shutdown_lines)}
"""
                            print(f"[DEBUG] Sending email: {subject}", flush=True)
                            emailer.sendEmail(subject, body)

                        if config['error']['log']:
                            for line in shutdown_lines:
                                log_event("ERROR", line)
                    return

                # === Detect Custom Keywords ===
                elif any(kw.lower() in line_lower for kw in config['custom']['keywords']):
                    if config['custom']['notify']:
                        subject = "❓ Klipper Log Match (Custom Keyword)"
                        body = f"""Your printer log matched a custom keyword.

Device: {DEVICE_NAME}
IP: {LOCAL_IP}
Time: {current_time_str()}

Matched line:
{line.strip()}
"""
                        print(f"[DEBUG] Sending email: {subject}", flush=True)
                        emailer.sendEmail(subject, body)
                    if config['custom']['log']:
                        log_event("CUSTOM", line.strip())

    except Exception as e:
        error_message = f"Exception occurred: {type(e).__name__}: {e}"
        print(f"❌ {error_message}")
        log_event("SCRIPT_ERROR", error_message)
        emailer.sendException(e)

if __name__ == "__main__":
    monitor_klipper_log()
