#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import argparse
import json
import os
import sys
import subprocess
import random
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def log_debug(message, data=None):
    """Log debug information to a separate debug file."""
    debug_log_file = os.path.join(os.getcwd(), 'logs', 'notification_debug.log')
    os.makedirs(os.path.dirname(debug_log_file), exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    with open(debug_log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
        if data:
            f.write(f"  Data: {json.dumps(data, indent=2)}\n")


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"
    
    log_debug("Checking TTS script availability")
    log_debug(f"Script directory: {script_dir}")
    log_debug(f"TTS directory: {tts_dir}")
    
    # Check for ElevenLabs API key (highest priority)
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    if elevenlabs_key:
        log_debug(f"ElevenLabs API key found (length: {len(elevenlabs_key)})")
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            log_debug(f"ElevenLabs script found: {elevenlabs_script}")
            return str(elevenlabs_script)
        else:
            log_debug(f"ElevenLabs script NOT found at: {elevenlabs_script}")
    else:
        log_debug("No ElevenLabs API key found")
    
    # Check for OpenAI API key (second priority)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        log_debug(f"OpenAI API key found (length: {len(openai_key)})")
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            log_debug(f"OpenAI script found: {openai_script}")
            return str(openai_script)
        else:
            log_debug(f"OpenAI script NOT found at: {openai_script}")
    else:
        log_debug("No OpenAI API key found")
    
    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        log_debug(f"pyttsx3 script found: {pyttsx3_script}")
        return str(pyttsx3_script)
    else:
        log_debug(f"pyttsx3 script NOT found at: {pyttsx3_script}")
    
    log_debug("No TTS scripts available!")
    return None


def announce_notification():
    """Announce that the agent needs user input."""
    try:
        log_debug("Starting announce_notification")
        
        tts_script = get_tts_script_path()
        if not tts_script:
            log_debug("No TTS script available, returning")
            return  # No TTS scripts available
        
        # Get engineer name if available
        engineer_name = os.getenv('ENGINEER_NAME', '').strip()
        log_debug(f"Engineer name: '{engineer_name}'")
        
        # Create notification message with 30% chance to include name
        random_value = random.random()
        log_debug(f"Random value for name inclusion: {random_value}")
        
        if engineer_name and random_value < 0.3:
            notification_message = f"{engineer_name}, your agent needs your input"
        else:
            notification_message = "Your agent needs your input"
        
        log_debug(f"Notification message: '{notification_message}'")
        
        # Call the TTS script with the notification message
        cmd = ["uv", "run", tts_script, notification_message]
        log_debug(f"Running command: {cmd}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,  # Capture output
            text=True,
            timeout=10  # 10-second timeout
        )
        
        log_debug(f"Command exit code: {result.returncode}")
        if result.stdout:
            log_debug(f"Command stdout: {result.stdout}")
        if result.stderr:
            log_debug(f"Command stderr: {result.stderr}")
        
    except subprocess.TimeoutExpired as e:
        log_debug(f"TTS command timed out: {e}")
    except subprocess.SubprocessError as e:
        log_debug(f"Subprocess error: {e}")
    except FileNotFoundError as e:
        log_debug(f"File not found error: {e}")
    except Exception as e:
        log_debug(f"Unexpected error in announce_notification: {type(e).__name__}: {e}")


def main():
    try:
        log_debug("=== Starting notification hook ===")
        
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--notify', action='store_true', help='Enable TTS notifications')
        args = parser.parse_args()
        
        log_debug(f"Arguments: notify={args.notify}")
        
        # Read JSON input from stdin
        stdin_data = sys.stdin.read()
        log_debug(f"Raw stdin data: {stdin_data[:200]}...")  # First 200 chars
        
        input_data = json.loads(stdin_data)
        log_debug("Input data parsed successfully", input_data)
        
        # Ensure log directory exists
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'notification.json')
        
        # Read existing log data or initialize empty list
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    log_data = json.load(f)
                    log_debug(f"Loaded {len(log_data)} existing log entries")
                except (json.JSONDecodeError, ValueError) as e:
                    log_debug(f"Error loading existing log: {e}")
                    log_data = []
        else:
            log_debug("No existing log file, starting fresh")
            log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        log_debug(f"Wrote {len(log_data)} entries to log file")
        
        # Announce notification via TTS only if --notify flag is set
        message = input_data.get('message', '')
        log_debug(f"Message: '{message}'")
        log_debug(f"Should announce: notify={args.notify}, message_not_default={message != 'Claude is waiting for your input'}")
        
        if args.notify and message != 'Claude is waiting for your input':
            log_debug("Calling announce_notification")
            announce_notification()
        else:
            log_debug("Skipping TTS announcement")
        
        log_debug("=== Notification hook completed successfully ===")
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        log_debug(f"JSON decode error: {e}")
        sys.exit(0)
    except Exception as e:
        log_debug(f"Unexpected error in main: {type(e).__name__}: {e}")
        sys.exit(0)

if __name__ == '__main__':
    main()