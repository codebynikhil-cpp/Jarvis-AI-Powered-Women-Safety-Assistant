import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values
import time
import aiohttp
from aiohttp import ClientTimeout
import platform

def _log_tts(message: str) -> None:
    try:
        os.makedirs("Data", exist_ok=True)
        with open(r"Data/tts_debug.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception:
        pass

def _local_tts_sapi5(text: str) -> bool:
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('volume', 1.0)
        # Optional: try set a common English voice if available
        try:
            for v in engine.getProperty('voices'):
                if 'English' in v.name or 'en_' in v.id.lower() or 'sapi5' in v.id.lower():
                    engine.setProperty('voice', v.id)
                    break
        except Exception:
            pass
        engine.say(text)
        engine.runAndWait()
        _log_tts("Spoken via pyttsx3 (offline) fallback")
        return True
    except Exception as e:
        _log_tts(f"pyttsx3 fallback failed: {e}")
        return False

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-GuyNeural")

async def TextToAudioFile(text, max_retries=3) -> None:
    try:
        file_path = r"Data/speech.mp3"
        os.makedirs("Data", exist_ok=True)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        # Configure timeout and retry settings
        timeout = ClientTimeout(total=30)  # 30 seconds timeout
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    # Request WAV/PCM output for maximum Windows compatibility
                    communicate = edge_tts.Communicate(
                        text,
                        AssistantVoice,
                        pitch='+5Hz',
                        rate='+13%'
                    )
                    await communicate.save(file_path)
                    _log_tts("Audio file generated successfully: Data/speech.mp3")
                    return True
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retry {retry_count}/{max_retries} for TTS generation...")
                    _log_tts(f"Retry {retry_count}/{max_retries} for TTS generation due to: {e}")
                    await asyncio.sleep(1)  # Wait 1 second before retrying
                continue

        print(f"Error in TextToAudioFile after {max_retries} retries: {last_error}")
        _log_tts(f"Failed to generate audio after retries: {last_error}")
        return False

    except Exception as e:
        print(f"Error in TextToAudioFile: {e}")
        return False

def TTS(Text, func=lambda r=None: True):
    try:
        # Ensure reliable audio driver on Windows
        if platform.system() == "Windows":
            os.environ.setdefault("SDL_AUDIODRIVER", "directsound")

        # Initialize pygame mixer with robust settings
        init_succeeded = False
        init_errors = []
        mixer_kwargs = {"frequency": 16000, "size": -16, "channels": 1, "buffer": 1024}
        try:
            pygame.mixer.init(**mixer_kwargs)
            init_succeeded = True
        except Exception as e_first:
            init_errors.append((os.environ.get("SDL_AUDIODRIVER"), str(e_first)))
            # Try alternate Windows drivers if available
            if platform.system() == "Windows":
                for driver in ["wasapi", "winmm", "directsound"]:
                    try:
                        os.environ["SDL_AUDIODRIVER"] = driver
                        pygame.mixer.init(**mixer_kwargs)
                        init_succeeded = True
                        break
                    except Exception as e_alt:
                        init_errors.append((driver, str(e_alt)))

        if not init_succeeded:
            _log_tts(f"pygame.mixer.init failed for drivers: {init_errors}")
            raise RuntimeError(f"Audio init failed: {init_errors}")
        
        # Wait for the audio file to be generated
        max_retries = 30  # wait up to ~3s
        retry_count = 0
        while retry_count < max_retries:
            if os.path.exists(r"Data/speech.mp3"):
                break
            retry_count += 1
            pygame.time.wait(100)  # Wait 100ms between retries
        
        if not os.path.exists(r"Data/speech.mp3"):
            print("Error: Audio file not generated")
            _log_tts("Audio file not found at playback time")
            return False

        # Load and play the audio
        pygame.mixer.music.load(r"Data/speech.mp3")
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()
        _log_tts("Playback started via pygame.mixer.music")

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            pygame.time.Clock().tick(10)
        
        _log_tts("Playback finished via pygame")
        return True

    except Exception as e:
        print(f"Error in TTS (pygame path): {e}")
        _log_tts(f"Error in TTS (pygame): {e}")
        # Fallbacks if playback fails
        try:
            # As a last resort, try offline pyttsx3
            _local_tts_sapi5(Text)
            return True
        except Exception as e_fallback:
            print(f"Fallback audio playback failed: {e_fallback}")
            _log_tts(f"Fallback playsound failed: {e_fallback}")
        return False

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    if not Text:
        return

    try:
        # Generate audio file with retries
        success = False
        max_attempts = 3
        attempt = 0
        
        while not success and attempt < max_attempts:
            success = asyncio.run(TextToAudioFile(Text))
            if not success:
                attempt += 1
                if attempt < max_attempts:
                    print(f"Retrying TTS generation (Attempt {attempt + 1}/{max_attempts})...")
                    time.sleep(1)  # Wait 1 second between attempts
                else:
                    print("Failed to generate audio file after multiple attempts")
                    _log_tts("Falling back to offline pyttsx3 due to generation failure")
                    if _local_tts_sapi5(Text):
                        return
                    return

        # Split text for long responses
        Data = str(Text).split(".")
        responses = [
            "The rest of the result has been printed to the chat screen, kindly check it out sir.",
            "The rest of the text is now on the chat screen, sir, please check it.",
            "You can see the rest of the text on the chat screen, sir.",
            "The remaining part of the text is now on the chat screen, sir.",
            "Sir, you'll find more text on the chat screen for you to see.",
            "The rest of the answer is now on the chat screen, sir.",
            "Sir, please look at the chat screen, the rest of the answer is there.",
            "You'll find the complete answer on the chat screen, sir.",
            "The next part of the text is on the chat screen, sir.",
            "Sir, please check the chat screen for more information."
        ]

        if len(Data) > 4 and len(Text) >= 250:
            # For long responses, speak the first part and notify about the rest
            first_part = " ".join(Text.split(".")[0:2]) + ". " + random.choice(responses)
            success = asyncio.run(TextToAudioFile(first_part))
            if success:
                TTS(first_part, func)
        else:
            # For shorter responses, speak the entire text
            TTS(Text, func)

    except Exception as e:
        print(f"Error in TextToSpeech: {e}")
        _log_tts(f"Error in TextToSpeech wrapper: {e}")
        # Final fallback to offline pyttsx3 if everything else failed silently
        _local_tts_sapi5(Text)

if __name__ == "__main__":
    while True:
        try:
            Answer = input("Enter the text: ")
            if Answer.strip():
                TextToSpeech(Answer)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")