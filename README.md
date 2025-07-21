
# Encrypted Keylogger PoC with Telegram Bot Exfiltration

## Project Overview

This Proof-of-Concept (PoC) project demonstrates a keylogger that captures keystrokes, encrypts the data (optional plain version supported), and exfiltrates it via a Telegram bot. The logs and screenshots are automatically deleted after sending. The tool includes persistence, a kill switch, and Telegram-based remote control.

---

## Features

- **Keystroke Capture** using `pynput`
- **Timed Log Rotation** (Every 10 seconds)
- **Telegram Bot Integration** for Exfiltration
- **Remote Commands**:
  - `/activate` — Start keylogging
  - `/deactivate` — Stop keylogging
  - `/status` — Check keylogger status
  - `/exit` — Kill the script
- **Screenshots every 10 sec** (auto-deleted after send)
---

## Prerequisites

Python 3.7 or later

### Required Libraries

Install them via pip:

```bash
pip install pynput cryptography pyautogui requests
```

---

## Telegram Bot Setup

1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Use `/newbot` to create a new bot.
3. Note the **API token** provided.
4. Send a message to your bot.
5. Use the `get_chat_id.py` script to obtain your `chat_id`.

---

## Scripts

### 1. `chatid.py`

```python
import requests

token = "YOUR_BOT_TOKEN_HERE"
updates = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
print(updates.json())
```

Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token and run the script to find your `chat_id`.

---

### 2. `main.py`

- Add your `bot_token` and `chat_id` at the top of the script.
- This script runs in the background and performs all the main functions (logging, screenshotting, exfiltration, control, etc.).
- The keylogger will start at boot due to the added registry entry.

To convert to `.exe` for persistence:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile main_keylogger.py
```

---

## Notes

- Make sure to allow Telegram bot access through firewall if needed.
- Logs and screenshots are auto-deleted after sending to maintain stealth.
- Test persistence by restarting your system after building the executable.

---

## Ethical Usage

This project is for educational and ethical purposes **only**. Do not use it to monitor or spy on anyone without their informed consent.


👤 Project Owner
Shubham Dongare(SHUBH) – Developer and Security Enthusiast
This project was created as part of an internship assignment for educational and ethical demonstration purposes only.
