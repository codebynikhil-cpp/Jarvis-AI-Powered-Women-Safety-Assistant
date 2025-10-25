from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import json
import os
import datetime

# Load environment variables
env_vars = dotenv_values(".env")
USERNAME = env_vars.get("Username", "User")
ASSISTANTNAME = env_vars.get("Assistantname", "JARVIS")
GroqAPIKey = env_vars.get("GROQ_API_KEY")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey not found in .env file")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Constants
SYSTEM_PROMPT = f"""You are {ASSISTANTNAME}, an advanced AI assistant for {USERNAME}. Provide accurate, professional responses.
- Use proper grammar and punctuation
- Be concise (1-2 sentences)
- For factual questions, include key information
- Skip unnecessary greetings"""

CHAT_LOG_PATH = os.path.join("Data", "ChatLog.json")
os.makedirs("Data", exist_ok=True)

# Initialize chat history
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []

def get_instant_response(prompt):
    """Handle common queries instantly without API calls"""
    prompt_lower = prompt.lower()
    if any(g in prompt_lower for g in ['hi', 'hello', 'hey']):
        return "Hello."
    elif any(g in prompt_lower for g in ['bye', 'exit', 'quit']):
        return "Goodbye!"
    elif 'how are you' in prompt_lower:
        return "I'm functioning optimally."
    elif 'time' in prompt_lower:
        return datetime.datetime.now().strftime("Current time: %H:%M")
    elif 'date' in prompt_lower:
        return datetime.datetime.now().strftime("Today's date: %d %B %Y")
    return None

def google_search(query, timeout=1.5):
    """Fast Google search with strict timeout"""
    try:
        search(query)
        return "Search completed."
    except Exception as e:
        return f"Search error: {str(e)}"

def content_writer(topic):
    """Generate content using AI and open in notepad"""
    try:
        topic = topic.replace("content ", "")
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": topic}],
            max_tokens=2048,
            temperature=0.7
        )
        
        content = completion.choices[0].message.content
        filename = os.path.join("Data", f"{topic.lower().replace(' ', '')}.txt")
        
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        
        subprocess.Popen(["notepad.exe", filename])
        return "Content created and opened in Notepad."
    except Exception as e:
        return f"Error creating content: {str(e)}"

def open_app(app):
    """Open application with smart fallback to web version"""
    try:
        # Clean up the app name and extract search query if any
        app_parts = app.strip().lower().split()
        app_name = app_parts[0]
        search_query = ' '.join(app_parts[1:]) if len(app_parts) > 1 else ''

        # Special handling for YouTube
        if 'youtube' in app_name:
            if search_query:
                url = f"https://www.youtube.com/results?search_query={search_query}"
            else:
                url = "https://www.youtube.com"
            webbrowser.open(url)
            return f"Opened YouTube{' and searching for ' + search_query if search_query else ''}"

        # First try to open local app
        try:
            appopen(app_name, match_closest=True, output=False)
            return f"Opened {app_name}"
        except:
            # Common web services and their URLs
            web_apps = {
                "whatsapp": "https://web.whatsapp.com",
                "spotify": "https://open.spotify.com",
                "netflix": "https://www.netflix.com",
                "gmail": "https://mail.google.com",
                "maps": "https://maps.google.com",
                "drive": "https://drive.google.com",
                "amazon": "https://www.amazon.in",
                "facebook": "https://www.facebook.com",
                "instagram": "https://www.instagram.com",
                "twitter": "https://twitter.com",
                "linkedin": "https://www.linkedin.com",
                "discord": "https://discord.com/app"
            }
            
            # Check if it's a known web app
            if app_name in web_apps:
                webbrowser.open(web_apps[app_name])
                return f"Opened {app_name} in web browser"
            
            # If not found, try a Google search
            search_url = f"https://www.google.com/search?q={app}"
            webbrowser.open(search_url)
            return f"Searching for {app} on Google"
            
    except Exception as e:
        return f"Error opening {app}: {str(e)}"

def close_app(app):
    """Close specified application"""
    try:
        close(app, match_closest=True, output=False)
        return f"Closed {app}"
    except Exception as e:
        return f"Couldn't close {app}"

def system_command(command):
    """Execute system volume controls"""
    cmd_map = {
        "mute": "volume mute",
        "unmute": "volume mute",
        "volume up": "volume up",
        "volume down": "volume down"
    }
    if command in cmd_map:
        keyboard.press_and_release(cmd_map[command])
        return f"Executed: {command}"
    return "Unknown system command"

async def execute_command(command):
    """Execute a single command asynchronously"""
    try:
        if not command:
            return ""
            
        command_lower = command.lower()
        
        # Check for instant responses first
        if response := get_instant_response(command):
            return response
            
        # Handle specific commands
        if command_lower.startswith("open "):
            return await asyncio.to_thread(open_app, command[5:])
        elif command_lower.startswith("close "):
            return await asyncio.to_thread(close_app, command[6:])
        elif command_lower.startswith("play "):
            playonyt(command[5:])
            return f"Playing {command[5:]} on YouTube"
        elif command_lower.startswith("content "):
            return await asyncio.to_thread(content_writer, command)
        elif command_lower.startswith("google search "):
            return await asyncio.to_thread(google_search, command[14:])
        elif command_lower.startswith("youtube search "):
            webbrowser.open(f"https://www.youtube.com/results?search_query={command[15:]}")
            return f"Searching YouTube for {command[15:]}"
        elif command_lower.startswith("system "):
            return await asyncio.to_thread(system_command, command[7:])
        else:
            # Handle conversational queries
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": command}],
                max_tokens=100,
                temperature=0.7
            )
            return completion.choices[0].message.content
            
    except Exception as e:
        return f"Error: {str(e)}"

async def Automation(commands: list) -> None:
    """
    Handle automation commands like opening/closing apps, playing videos, etc.
    
    Args:
        commands (list): List of commands to execute
    """
    for command in commands:
        try:
            if command.startswith("open "):
                app_name = command.replace("open ", "").strip()
                appopen(app_name)
                await asyncio.sleep(0.5)  # Small delay between commands
                
            elif command.startswith("close "):
                app_name = command.replace("close ", "").strip()
                close(app_name)
                await asyncio.sleep(0.5)
                
            elif command.startswith("play "):
                query = command.replace("play ", "").strip()
                playonyt(query)
                await asyncio.sleep(0.5)
                
            elif command.startswith("google search "):
                query = command.replace("google search ", "").strip()
                search(query)
                await asyncio.sleep(0.5)
                
            elif command.startswith("youtube search "):
                query = command.replace("youtube search ", "").strip()
                webopen(f"https://www.youtube.com/results?search_query={query}")
                await asyncio.sleep(0.5)
                
        except Exception as e:
            print(f"Error executing command '{command}': {e}")
            continue

def Automation(commands: list) -> None:
    """
    Synchronous wrapper for the async Automation function
    """
    asyncio.run(_Automation(commands))

async def _Automation(commands: list) -> None:
    """
    Internal async implementation of Automation
    """
    for command in commands:
        try:
            if command.startswith("open "):
                app_name = command.replace("open ", "").strip()
                appopen(app_name)
                await asyncio.sleep(0.5)  # Small delay between commands
                
            elif command.startswith("close "):
                app_name = command.replace("close ", "").strip()
                close(app_name)
                await asyncio.sleep(0.5)
                
            elif command.startswith("play "):
                query = command.replace("play ", "").strip()
                playonyt(query)
                await asyncio.sleep(0.5)
                
            elif command.startswith("google search "):
                query = command.replace("google search ", "").strip()
                search(query)
                await asyncio.sleep(0.5)
                
            elif command.startswith("youtube search "):
                query = command.replace("youtube search ", "").strip()
                webopen(f"https://www.youtube.com/results?search_query={query}")
                await asyncio.sleep(0.5)
                
        except Exception as e:
            print(f"Error executing command '{command}': {e}")
            continue

async def main():
    print(f"{ASSISTANTNAME}: Ready. How can I assist you today?")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ('exit', 'quit', 'bye'):
                print(f"{ASSISTANTNAME}: Goodbye!")
                break
                
            response = await execute_command(user_input)
            print(f"{ASSISTANTNAME}: {response}")
            
        except KeyboardInterrupt:
            print(f"\n{ASSISTANTNAME}: Session ended.")
            break
        except Exception as e:
            print(f"{ASSISTANTNAME}: An error occurred - {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
    # Test the automation
    test_commands = [
        "open chrome",
        "play never gonna give you up",
        "google search python programming",
        "youtube search coding tutorials"
    ]
    Automation(test_commands)