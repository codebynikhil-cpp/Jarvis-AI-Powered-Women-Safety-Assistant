from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import Chatbot
from Backend.TextToSpeech import TextToSpeech
from Backend.WhatsAppAutomation import send_emergency_alert
import sounddevice as sd
import soundfile as sf
import geocoder
import time
from datetime import datetime
from dotenv import dotenv_values
from asyncio import run
from time import sleep


import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = "Jarvis AI"  # Changed from JARVIS to Jarvis AI
AssistantVoice = env_vars.get("AssistantVoice", "en-US-GuyNeural")
InputLanguage = env_vars.get("InputLanguage", "en-US")
GroqAPIKey = env_vars.get("GROQ_API_KEY")


# Validate required environment variables
if not Username:
    print("Warning: Username not found in .env file. Using default: User")

DefaultMessage = f'''{Username} : Hello JARVIS, How are you?
JARVIS : Greetings {Username}. I am JARVIS, your advanced AI assistant. How may I assist you today?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
#Nikhil
# Initialize Chatbot instance
chatbot = Chatbot()

# Function to show default chat if no chats exist
def ShowDefaultChatIfNoChats():
    os.makedirs("Data", exist_ok=True)
    if not os.path.exists(r'Data\Chatlog.json'):
        with open(r'Data\Chatlog.json', "w", encoding='utf-8') as file:
            json.dump([], file)
    
    with open(r'Data\Chatlog.json', "r", encoding='utf-8') as file:
        if len(file.read()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")

            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)

# Function to read chat log JSON
def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except json.JSONDecodeError:
        return []

# Function to integrate chat log
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

# Function to show chats on GUI
def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            Data = file.read()
            if len(str(Data)) > 0:
                lines = Data.split('\n')
                result = '\n'.join(lines)
                with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                    file.write(result)
    except Exception as e:
        print(f"Error showing chats: {e}")

# Function to get current location details
def get_current_location():
    """Get current location details"""
    try:
        g = geocoder.ip('me')
        if g.ok:
            return {
                'address': f"{g.city}, {g.state}, {g.country}",
                'coordinates': (g.lat, g.lng)
            }
    except Exception as e:
        print(f"Error getting location: {e}")
    return None

# Function to record audio for emergency
def record_emergency_audio(duration=10):
    """Record audio for specified duration"""
    try:
        print("Recording emergency audio...")
        recording = sd.rec(int(duration * 44100), samplerate=44100, channels=2)
        sd.wait()
        
        # Save recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emergency_audio_{timestamp}.wav"
        filepath = os.path.join("Data", "Emergency", filename)
        os.makedirs(os.path.join("Data", "Emergency"), exist_ok=True)
        
        sf.write(filepath, recording, 44100)
        return filepath
    except Exception as e:
        print(f"Error recording audio: {e}")
        return None

# Initial execution setup
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

# Main execution function
def MainExecution(Query=None):
    while True:  # Added continuous loop
        if not Query:
            SetAssistantStatus("Listening...")
            Query = SpeechRecognition()
            if not Query:
                continue  # Continue listening instead of returning
        
        # Check for emergency keywords
        emergency_keywords = ["help", "save", "emergency", "danger", "scared", "unsafe"]
        if any(keyword in Query.lower() for keyword in emergency_keywords):
            SetAssistantStatus("Emergency Detected!")
            ShowTextToScreen("🚨 EMERGENCY MODE ACTIVATED - Recording audio...")
            
            # Get location
            location = get_current_location()
            if not location:
                ShowTextToScreen("Warning: Could not get location!")
                return True
                
            # Record audio
            audio_file = record_emergency_audio(10)  # 10 seconds recording
            if not audio_file:
                ShowTextToScreen("Warning: Could not record audio!")
                return True
                
            # Send emergency alert
            ShowTextToScreen("Sending emergency alert...")
            success = send_emergency_alert(location, audio_file)
            
            if success:
                ShowTextToScreen("Emergency alert sent successfully!")
            else:
                ShowTextToScreen("Failed to send emergency alert!")
                
            Query = None  # Reset Query to enable new listening
            continue

        ShowTextToScreen(f"{Username}: {Query}")
        SetAssistantStatus("Thinking...")
        Decision = FirstLayerDMM(Query)
        
        if not Decision:
            Query = None  # Reset Query to enable new listening
            continue

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])
        A = any([i for i in Decision if any(i.startswith(func) for func in Functions)])

        if A:
            # Handle automation commands
            SetAssistantStatus("Executing...")
            try:
                run(Automation(Decision))
            except Exception as e:
                print(f"Error in Automation: {e}")
            Query = None  # Reset Query to enable new listening
            continue

        if R:
            # Handle real-time queries
            SetAssistantStatus("Searching...")
            try:
                Answer = RealtimeSearchEngine(Query)
                if Answer:
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
            except Exception as e:
                print(f"Error in RealtimeSearchEngine: {e}")
            Query = None  # Reset Query to enable new listening
            continue
        
        if G:
            # Handle general queries
            SetAssistantStatus("Thinking...")
            try:
                Answer = chatbot.chat(QueryModifier(Query))
                if Answer:
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
            except Exception as e:
                print(f"Error in Chatbot: {e}")
            Query = None  # Reset Query to enable new listening
            continue

# Thread to handle microphone input
def FirstThread():
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            if CurrentStatus == "True":
                MainExecution()
            else:
                AIStatus = GetAssistantStatus()
                if "Listening..." in AIStatus:  # Changed from "Available..." to "Listening..."
                    sleep(0.1)
                else:
                    SetAssistantStatus("Listening...")  # Changed from "Available..." to "Listening..."
        except Exception as e:
            print(f"Error in FirstThread: {e}")
            SetAssistantStatus("Listening...")  # Changed from "Available..." to "Listening..."
            sleep(1)

# Thread to handle GUI
def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in SecondThread: {e}")

# Main execution
if __name__ == "__main__":
    try:
        thread2 = threading.Thread(target=FirstThread, daemon=True)
        thread2.start()
        SecondThread()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        for process in subprocesses:
            try:
                process.terminate()
            except:
                pass