#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "elevenlabs",
#     "python-dotenv",
# ]
# ///

import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
if not api_key:
    print("No ElevenLabs API key found")
    exit(1)

client = ElevenLabs(api_key=api_key)

print("Available voices:")
print("-" * 40)

try:
    voices = client.voices.get_all()
    for voice in voices.voices[:10]:  # Show first 10 voices
        print(f"Name: {voice.name}")
        print(f"ID: {voice.voice_id}")
        print(f"Category: {voice.category}")
        print("-" * 40)
except Exception as e:
    print(f"Error fetching voices: {e}")