import asyncio
import httpx
import os
from typing import List
import traceback
from tenacity import retry, stop_after_attempt, wait_exponential

# Ensure the backend service is running, e.g., using: uvicorn app.main:app --reload --port 8000
BASE_URL = "http://127.0.0.1:8000"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def make_api_request(client: httpx.AsyncClient, endpoint: str, json_data: dict) -> dict:
    """Make API request with retry mechanism"""
    try:
        response = await client.post(endpoint, json=json_data)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        raise

async def test_frontend_integration():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=180.0) as client:  # Increased timeout
        print("--- Backend Frontend Integration Test Started ---")

        # --- Test Scenario 1: Basic Audio Generation (Simulating MainScreen direct input) ---
        print("\n--- Scenario 1: Basic Audio Generation ---")
        description_1 = "Raindrops on leaves, accompanied by distant bird calls"
        print(f"Simulating user description: \"{description_1}\"")
        # Audio generation test moved to another file

        # --- Test Scenario 2: Poem Conversion & Generation (Simulating Onboarding 'story' -> MainScreen poem -> ChatScreen generate) ---
        print("\n--- Scenario 2: Poem Conversion & Generation ---")
        poem_description = "A small building, listening to spring rain all night"
        print(f"Simulating user input poem: \"{poem_description}\" (Mode: story)")
        try:
            # Simulate ChatScreen calling generate-scene for poem conversion
            scene_request_2 = {
                "prompt": poem_description,
                "mode": "story",
                "chat_history": []
            }
            scene_data_2 = await make_api_request(client, "/api/generate-scene", scene_request_2)
            print(f"Scenario 2 Poem Conversion AI Response: {scene_data_2.get('response')}, Should Generate Audio: {scene_data_2.get('should_generate_audio')}")
            
            # If should_generate_audio is True, proceed with audio generation
            if scene_data_2.get('should_generate_audio'):
                audio_request = {
                    "description": poem_description,
                    "duration": 5,
                    "is_poem": True
                }
                audio_data = await make_api_request(client, "/api/generate-audio", audio_request)
                print(f"Audio generation response: {audio_data}")
                
        except Exception as e:
            print(f"Scenario 2 Error: {str(e)}")
            print(f"Detailed error: {traceback.format_exc()}")
            raise

        # --- Test Scenario 3: Guided Conversation & Final Generation (Simulating Onboarding mode -> MainScreen initial input -> ChatScreen conversation -> Generate) ---
        print("\n--- Scenario 3: Guided Conversation & Final Generation ---")
        initial_chat_input = "I want a quiet and relaxing soundscape."
        chat_history: List[str] = []
        current_mode = "relax" # Assume passed from Onboarding

        print(f"Simulating initial chat input: \"{initial_chat_input}\" (Mode: {current_mode})")
        try:
            # 1. Simulate ChatScreen initial call to generate-scene
            scene_request_3_1 = {
                "prompt": initial_chat_input,
                "mode": current_mode,
                "chat_history": chat_history
            }
            scene_response_3_1 = await client.post("/api/generate-scene", json=scene_request_3_1)
            scene_response_3_1.raise_for_status()
            scene_data_3_1 = scene_response_3_1.json()
            chat_history.append(initial_chat_input) # Update chat history
            print(f"AI Response 1: {scene_data_3_1.get('response')}")

            # 2. Simulate user selecting atmosphere
            user_atmosphere = "Cozy and intimate"
            print(f"User selects atmosphere: \"{user_atmosphere}\"")
            chat_history.append(f"Atmosphere: {user_atmosphere}") # Simulate adding selection to history

            scene_request_3_2 = {
                "prompt": f"I chose atmosphere: {user_atmosphere}", # Simulate user sending selection
                "mode": current_mode,
                "chat_history": chat_history
            }
            scene_response_3_2 = await client.post("/api/generate-scene", json=scene_request_3_2)
            scene_response_3_2.raise_for_status()
            scene_data_3_2 = scene_response_3_2.json()
            print(f"AI Response 2: {scene_data_3_2.get('response')}")

            # 3. Simulate user selecting mood
            user_mood = "Relaxed"
            print(f"User selects mood: \"{user_mood}\"")
            chat_history.append(f"Mood: {user_mood}")

            scene_request_3_3 = {
                "prompt": f"I chose mood: {user_mood}",
                "mode": current_mode,
                "chat_history": chat_history
            }
            scene_response_3_3 = await client.post("/api/generate-scene", json=scene_request_3_3)
            scene_response_3_3.raise_for_status()
            scene_data_3_3 = scene_response_3_3.json()
            print(f"AI Response 3: {scene_data_3_3.get('response')}")

            # 4. Simulate user selecting elements
            user_elements = ["Rain", "Birds chirping"]
            print(f"User selects elements: {user_elements}")
            chat_history.append(f"Elements: {', '.join(user_elements)}")

            scene_request_3_4 = {
                "prompt": f"I want these elements: {', '.join(user_elements)}",
                "mode": current_mode,
                "chat_history": chat_history
            }
            scene_response_3_4 = await client.post("/api/generate-scene", json=scene_request_3_4)
            scene_response_3_4.raise_for_status()
            scene_data_3_4 = scene_response_3_4.json()
            print(f"AI Response 4: {scene_data_3_4.get('response')}")

            # 5. Simulate user sending final generation command
            final_generate_prompt = "Okay, generate the audio now."
            print(f"User issues generation command: \"{final_generate_prompt}\"")
            chat_history.append(final_generate_prompt)

            scene_request_3_5 = {
                "prompt": final_generate_prompt,
                "mode": current_mode,
                "chat_history": chat_history
            }
            scene_response_3_5 = await client.post("/api/generate-scene", json=scene_request_3_5)
            scene_response_3_5.raise_for_status()
            scene_data_3_5 = scene_response_3_5.json()
            print(f"AI Response 5: {scene_data_3_5.get('response')}, Should Generate Audio: {scene_data_3_5.get('should_generate_audio')}")
        except Exception as e:
            print(f"Scenario 3 Conversation Error: {traceback.format_exc()}")

        print("\n--- Backend Frontend Integration Test Finished ---")

if __name__ == "__main__":
    asyncio.run(test_frontend_integration()) 