# Printer Monitor Script

This repository contains a script to monitor Klipper logs for specific events (such as print pauses, completions, and errors) and send email notifications. The script runs on a system with Klipper and is triggered at the start of each print.

## Features

- Monitors Klipper logs for key events such as print pauses, completions, and errors
- Sends email notifications with details including device name, local IP, and timestamp
- Logs events to a local log file
- Configurable via a TOML configuration file
- Automatically prevents multiple monitor instances from launching

## System Requirements and Dependencies

Before setting up the printer monitor script, ensure your system has the following dependencies installed.

### Required Packages

| Tool             | Purpose                                        |
|------------------|------------------------------------------------|
| `python3`        | Runs the monitor script                        |
| `pip`            | Installs Python libraries                      |
| `python3-dotenv` | Loads environment variables from `.env`        |
| `toml`           | Parses the `printer_monitor_config.toml` file |
| `mailutils`      | (optional) CLI mail testing or system mail     |

### Check for Dependencies

Run the following commands to verify dependencies:

```bash
which python3
which pip
python3 -m pip show python-dotenv
python3 -m pip show toml
```

### Install Dependencies

Update your package lists first:

```bash
sudo apt update
```

Install Python and pip:

```bash
sudo apt install -y python3 python3-pip
```

Install required Python libraries:

```bash
pip3 install python-dotenv toml
```

Optionally, install `mailutils` for CLI email testing:

```bash
sudo apt install -y mailutils
```

## Components

- `printer_monitor.py`: Main script that watches Klipper logs and triggers notifications
- `start_monitor.sh`: Wrapper script to launch the monitor safely with environment setup
- `printer_monitor_config.toml`: Configuration for pause, resume, complete, and error detection
- `printer_monitor.env`: Stores sensitive SMTP credentials and recipient information
- `monitor_events.log`: Log file created by the monitor script to store local event history

## Setup Instructions

1. Clone the repository (or copy the script folder to your Pi or Klipper machine):

```bash
git clone https://github.com/yourusername/printer-monitor.git
cd printer-monitor
```

2. Create the `.env` file in the same directory as the script:

```ini
SMTP_EMAIL=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_TO=recipient@example.com
```

3. Edit the TOML config file `printer_monitor_config.toml` to match the keywords and behavior you want:

```toml
[pause]
keywords = ["pause print", "runout", "filament sensor"]
notify = true
log = true

[complete]
keywords = ["finished print", "print completed", "done", "finished sd card print", "print finished"]
notify = true
log = true

[resume]
keywords = ["print resumed", "print started"]
notify = false
log = true

[error]
keywords = ["shutdown", "klipper state: shutdown"]
notify = true
log = true

[custom]
keywords = ["start", "thermal runaway", "skipping steps", "clogged nozzle"]
notify = false
log = true
```

4. Make the wrapper script executable:

```bash
chmod +x start_monitor.sh
```

5. Add the following to your `printer.cfg` to allow Klipper to trigger the monitor:

```ini
[gcode_shell_command start_printer_monitor]
command: /home/sovol/printer_monitor/start_monitor.sh
timeout: 10.0
```

6. Add this command to your `print_start` macro or slicer G-code:

```gcode
RUN_SHELL_COMMAND CMD=start_printer_monitor
```

## Usage

Each time a print starts, Klipper will run the shell command to launch the monitor in the background. The monitor watches `klippy.log` and reacts to configured events.

Use this to confirm that it’s running:

```bash
pgrep -af printer_monitor.py
```

To make sure only one instance is active:

```bash
pgrep -fc printer_monitor.py
```

## Event Log

The monitor creates a log file at:

```
/home/sovol/printer_monitor/monitor_events.log
```

This file contains timestamps and tags for events like:

- [PAUSE]
- [COMPLETE]
- [ERROR]
- [CUSTOM]

## Troubleshooting

- If you do not receive emails, check the following:
  - Your `.env` values are correct
  - You are using a Gmail App Password (not a regular password)
  - `debug_output.log` shows any error output

To see script output:

```bash
tail -n 50 /home/sovol/printer_monitor/debug_output.log
```

## License

MIT License – Use and modify freely.
