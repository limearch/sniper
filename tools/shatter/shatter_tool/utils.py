# File: tools/shatter/shatter_tool/utils.py
# Description: Enhanced Session & Reporting (Detailed JSON).

import json
import os
import time
from pathlib import Path
from lib.sniper_env import env

SESSION_FILE = env.CACHE_DIR / "shatter_session.json"

def save_session(wordlist_path: str, offset: int, target_file: str):
    data = {
        "wordlist": str(wordlist_path),
        "offset": offset,
        "target": str(target_file),
        "timestamp": time.time()
    }
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass 

def load_session() -> dict:
    if not SESSION_FILE.exists():
        return None
    try:
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def clear_session():
    if SESSION_FILE.exists():
        os.remove(SESSION_FILE)

def save_report(target_data: dict, password: str, stats: dict, wordlist_path: str, output_file: str):
    """
    Saves a rich, detailed JSON report.
    """
    # Calculate file size of the wordlist if possible
    try:
        wl_size = os.path.getsize(wordlist_path)
    except:
        wl_size = 0

    report = {
        "status": "cracked",
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "target_metadata": {
            "filename": target_data.get("filename", "unknown"),
            "encryption": target_data.get("aes_info", {}).get("aes_strength_name", "Unknown"),
            "salt_hex": target_data.get("salt_hex", ""),
            "verifier_hex": target_data.get("password_verifier_hex", "")
        },
        "cracked_credential": {
            "password_text": password,
            "password_hex": password.encode().hex(),
            "length": len(password)
        },
        "attack_details": {
            "wordlist_path": os.path.abspath(wordlist_path),
            "wordlist_size_bytes": wl_size,
            "line_number_found": stats.get("total_tried", 0)
        },
        "performance_metrics": {
            "total_attempts": stats.get("total_tried", 0),
            "time_elapsed_sec": round(stats.get("time_taken", 0), 2),
            "average_speed_hash_per_sec": round(stats.get("avg_speed", 0), 2)
        }
    }
    
    try:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=4)
        env.log.success(f"Detailed report saved to [bold underline]{output_file}[/]")
    except Exception as e:
        env.log.error(f"Failed to save report: {e}")
