# Printer Monitor Script

This repository contains a script to monitor Klipper logs for specific events (such as print pauses, completions, and errors) and send email notifications. The script is triggered at the start of each print using Klipper's `gcode_shell_command`.

## Features

- Monitors `klippy.log` for key events like pauses, completions, shutdowns, and custom alerts
- Sends email notifications with hostname, IP address, and timestamp
- Writes local event history to `monitor_events.log`
- Automatically avoids duplicate instances of the monitor
- Configurable via a TOML config file

---

## System Requirements and Dependencies

Before installing, ensure the following are available on your Klipper system:

| Tool             | Purpose                                        |
|------------------|------------------------------------------------|
| `python3`        | Runs the monitor script                        |
| `pip`            | Installs Python libraries                      |
| `python3-dotenv` | Loads environment variables from `.env`        |
| `toml`           | Parses the TOML configuration file             |

### Install Dependencies

Update package list and install Python:

```bash
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install python-dotenv toml
```

---

## File Overview

This repository contains the following files:

- `printer_monitor.py`: Main script
- `printer_monitor_config.toml`: Keyword config
- `printer_monitor.env`: Email credentials (you must fill this in)
- `start_monitor.sh`: Wrapper to safely launch the script
- `email_notify/`: Git submodule (PythonEmailNotify) for reusable email logic

---

## Setup

### 1. Clone This Repo (with Submodules)

```bash
git clone --recurse-submodules https://github.com/killermelon1458/printer_monitor.git
cd printer_monitor
```

### 2. Create Your `.env` File

Copy `printer_monitor.env` and edit it to include your email info:

```env
SMTP_EMAIL=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_TO=recipient@example.com
```

> ⚠️ For Gmail, you must use an **App Password**, not your main password.

### 3. Make the Launcher Executable

```bash
chmod +x start_monitor.sh
```

---

## Integration with Klipper

To launch the script with every print, configure `printer.cfg`:

### Add to printer.cfg or Macro.cfg


```gcode
[gcode_shell_command start_printer_monitor]
command: /home/your_username/printer_monitor/start_monitor.sh
timeout: 5.0
verbose: False
```

> 💡 `timeout` must be greater than 0.0 to avoid Klipper errors.

### Add to print_start macro or slicer G-code:

```gcode
RUN_SHELL_COMMAND CMD=start_printer_monitor
```

This ensures the monitor starts at the beginning of every print.

---

## How It Works

The monitor watches `klippy.log` in real-time. It detects and logs:

- Pauses (`pause print`, `runout`)
- Resumes
- Completed prints (`finished sd card print`, etc.)
- Errors (`shutdown`)
- Custom keywords (e.g., `thermal runaway`, `start`)

It sends emails (if enabled in config) and writes local logs to `monitor_events.log`.

---

## Monitoring & Logs

### Check if the monitor is running:

```bash
pgrep -af printer_monitor.py
```

### Check how many instances:

```bash
pgrep -fc printer_monitor.py
```

### See event log:

```bash
tail -n 50 /home/sovol/printer_monitor/monitor_events.log
```

### See debug/error output:

```bash
tail -n 50 /home/sovol/printer_monitor/debug_output.log
```

---

## Credit

Python shell command integration with Klipper is made possible thanks to guidance from the [KIAUH project](https://github.com/dw-0/kiauh):

- [gcode_shell_command.py](https://github.com/dw-0/kiauh/blob/master/resources/gcode_shell_command.py)
- [gcode_shell_command documentation](https://github.com/dw-0/kiauh/blob/master/docs/gcode_shell_command.md)

---

## License

MIT License – Use, fork, and modify freely.
