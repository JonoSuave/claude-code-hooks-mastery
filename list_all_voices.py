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

print("🎙️  Available ElevenLabs Voices")
print("=" * 60)

try:
    voices = client.voices.get_all()
    
    # Group by category
    categories = {}
    for voice in voices.voices:
        category = voice.category if voice.category else "uncategorized"
        if category not in categories:
            categories[category] = []
        categories[category].append(voice)
    
    # Display by category
    for category, voice_list in sorted(categories.items()):
        print(f"\n📂 Category: {category.upper()}")
        print("-" * 60)
        for voice in sorted(voice_list, key=lambda x: x.name):
            labels = ", ".join(voice.labels.values()) if voice.labels else "No labels"
            print(f"  • {voice.name}")
            print(f"    ID: {voice.voice_id}")
            if voice.labels:
                print(f"    Labels: {labels}")
            print()
    
    print(f"\n📊 Total voices: {len(voices.voices)}")
    
except Exception as e:
    print(f"Error fetching voices: {e}")