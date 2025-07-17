import asyncio
import edge_tts

async def list_voices():
    voices = await edge_tts.list_voices()
    print("Available English US Female voices:")
    print("-" * 50)
    for voice in voices:
        if 'en-US' in voice['ShortName'] and voice['Gender'] == 'Female':
            print(f"{voice['ShortName']}: {voice['FriendlyName']}")
    print("\nRecommended soft voices for storytelling:")
    print("-" * 50)
    soft_voices = [
        'en-US-JennyNeural',  # Warm and friendly
        'en-US-SaraNeural',   # Gentle and clear
        'en-US-AriaNeural',   # Current default
        'en-US-DavisNeural',  # Soft male voice
        'en-US-GuyNeural',    # Warm male voice
    ]
    for voice_name in soft_voices:
        for voice in voices:
            if voice['ShortName'] == voice_name:
                print(f"{voice['ShortName']}: {voice['FriendlyName']}")
                break

if __name__ == "__main__":
    asyncio.run(list_voices()) 