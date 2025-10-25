import os
import sys
import time
import logging
import pyautogui
import subprocess
from datetime import datetime
import win32gui
import win32con
import win32process
import psutil
import pygetwindow as gw
import pywhatkit as kit
import webbrowser
import urllib.parse
import pyperclip

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def launch_whatsapp():
    """Launch WhatsApp if not running"""
    try:
        # Check if WhatsApp is already running
        for proc in psutil.process_iter(['name']):
            if 'whatsapp' in proc.info['name'].lower():
                logger.info("WhatsApp is already running")
                return True

        # Try different possible WhatsApp paths
        possible_paths = [
            os.path.expanduser("~\\AppData\\Local\\WhatsApp\\WhatsApp.exe"),
            "C:\\Program Files\\WhatsApp\\WhatsApp.exe",
            "C:\\Program Files (x86)\\WhatsApp\\WhatsApp.exe"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Launching WhatsApp from: {path}")
                subprocess.Popen(path)
                # Wait for WhatsApp to start
                time.sleep(10)
                return True

        logger.error("Could not find WhatsApp executable")
        return False
    except Exception as e:
        logger.error(f"Error launching WhatsApp: {e}")
        return False

def get_whatsapp_window():
    """Get WhatsApp window and ensure it's properly positioned"""
    try:
        # First try to launch WhatsApp if not running
        if not launch_whatsapp():
            return None

        # Try different window title variations
        possible_titles = ['WhatsApp', 'WhatsApp Desktop', 'WhatsApp.exe']
        window = None
        
        # Wait for window to appear
        max_attempts = 5
        for attempt in range(max_attempts):
            for title in possible_titles:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    window = windows[0]
                    break
            if window:
                break
            logger.info(f"Waiting for WhatsApp window... Attempt {attempt + 1}/{max_attempts}")
            time.sleep(2)
        
        if not window:
            # Try to find by process name
            for proc in psutil.process_iter(['name', 'pid']):
                if 'whatsapp' in proc.info['name'].lower():
                    # Get window handle from process
                    def callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            if pid == proc.info['pid']:
                                windows.append(hwnd)
                        return True
                    
                    windows = []
                    win32gui.EnumWindows(callback, windows)
                    if windows:
                        hwnd = windows[0]
                        # Convert handle to window object
                        window = gw.Window(hwnd)
                        break
        
        if not window:
            logger.error("WhatsApp window not found")
            return None
            
        # Ensure window is not minimized
        if window.isMinimized:
            window.restore()
        
        # Move window to a known position and size
        window.moveTo(0, 0)
        window.resizeTo(1200, 800)
        window.activate()
        
        # Give time for window to respond
        time.sleep(2)
        
        # Verify window is still valid
        if not window.isActive:
            logger.error("Failed to activate WhatsApp window")
            return None
            
        return window
    except Exception as e:
        logger.error(f"Error handling WhatsApp window: {e}")
        return None

def send_emergency_alert(location, audio_file=None):
    """Send emergency alert via WhatsApp"""
    try:
        # Emergency contact numbers
        numbers = ["+917760401421", "+916205245097"]
        
        # Create a more detailed emergency message
        message = f"""🚨 URGENT: EMERGENCY ALERT 🚨

          ⚠️ IMMEDIATE ATTENTION REQUIRED ⚠️

            This is an automated emergency alert from JARVIS AI Safety System.

            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Location: {location['address']}
            Maps: https://maps.app.goo.gl/oHbGFfHsw8oCGTTV8

            ⚠️ Possible distress situation detected:
            - Audio recording attached
            - Live location shared
            - Immediate response required

Please respond immediately and take necessary action.

This is an automated message from JARVIS AI Safety System."""
        
        success = False
        for number in numbers:
            try:
                # URL encode the message
                encoded_message = urllib.parse.quote(message)
                
                # Open WhatsApp Web directly with the message
                url = f"https://web.whatsapp.com/send?phone={number}&text={encoded_message}"
                webbrowser.open(url)
                logger.info(f"Opening WhatsApp Web for {number}")
                time.sleep(15)  # Increased wait time for WhatsApp Web to load
                
                # Try multiple methods to send the message
                message_sent = False
                for attempt in range(5):  # Try 5 times
                    try:
                        # Method 1: Direct click on send button (multiple positions)
                        send_positions = [
                            (1200, 700),  # Common position
                            (1150, 700),  # Slightly left
                            (1250, 700),  # Slightly right
                            (1200, 650),  # Slightly up
                            (1200, 750)   # Slightly down
                        ]
                        
                        for pos_x, pos_y in send_positions:
                            try:
                                # Move mouse to position
                                pyautogui.moveTo(pos_x, pos_y, duration=0.5)
                                time.sleep(0.5)
                                # Click
                                pyautogui.click()
                                time.sleep(2)
                                message_sent = True
                                break
                            except:
                                continue
                        
                        if message_sent:
                            break
                            
                        # Method 2: Using Enter key
                        pyautogui.press('enter')
                        time.sleep(2)
                        message_sent = True
                        break
                    except:
                        try:
                            # Method 3: Using Ctrl+Enter
                            pyautogui.hotkey('ctrl', 'enter')
                            time.sleep(2)
                            message_sent = True
                            break
                        except:
                            try:
                                # Method 4: Using Tab and Enter
                                pyautogui.press('tab')
                                time.sleep(0.5)
                                pyautogui.press('enter')
                                time.sleep(2)
                                message_sent = True
                                break
                            except:
                                time.sleep(1)
                
                if not message_sent:
                    logger.error("Failed to send message after multiple attempts")
                    continue
                
                logger.info(f"Emergency message sent to {number}")
                time.sleep(3)
                
                # Send live location
                try:
                    # Click attachment button (clip icon)
                    pyautogui.click(x=1000, y=700)
                    time.sleep(2)
                    
                    # Click location option
                    pyautogui.click(x=1000, y=500)
                    time.sleep(2)
                    
                    # Click "Share Live Location" option
                    pyautogui.click(x=1000, y=400)
                    time.sleep(2)
                    
                    # Select duration (8 hours)
                    pyautogui.click(x=1000, y=300)
                    time.sleep(2)
                    
                    # Send live location
                    location_sent = False
                    for attempt in range(5):  # Try 5 times
                        try:
                            # Try multiple positions for send button
                            for pos_x, pos_y in send_positions:
                                try:
                                    pyautogui.moveTo(pos_x, pos_y, duration=0.5)
                                    time.sleep(0.5)
                                    pyautogui.click()
                                    time.sleep(2)
                                    location_sent = True
                                    break
                                except:
                                    continue
                            
                            if location_sent:
                                break
                                
                            # Try Enter key
                            pyautogui.press('enter')
                            time.sleep(2)
                            location_sent = True
                            break
                        except:
                            try:
                                # Try Ctrl+Enter
                                pyautogui.hotkey('ctrl', 'enter')
                                time.sleep(2)
                                location_sent = True
                                break
                            except:
                                try:
                                    # Try Tab and Enter
                                    pyautogui.press('tab')
                                    time.sleep(0.5)
                                    pyautogui.press('enter')
                                    time.sleep(2)
                                    location_sent = True
                                    break
                                except:
                                    time.sleep(1)
                    
                    if not location_sent:
                        logger.error("Failed to send live location after multiple attempts")
                    
                    logger.info(f"Live location sent to {number}")
                    time.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Failed to send live location to {number}: {e}")
                
                # If audio file exists, try to send it
                if audio_file and os.path.exists(audio_file):
                    try:
                        logger.info(f"Attempting to send audio file: {audio_file}")
                        
                        # Click attachment button (clip icon)
                        pyautogui.click(x=1000, y=700)
                        time.sleep(2)
                        
                        # Click document option
                        pyautogui.click(x=1000, y=600)
                        time.sleep(2)
                        
                        # Copy file path to clipboard
                        abs_path = os.path.abspath(audio_file)
                        pyperclip.copy(abs_path)
                        
                        # Paste file path in file dialog
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(2)
                        pyautogui.press('enter')
                        time.sleep(5)  # Wait for file upload
                        
                        # Send the file
                        file_sent = False
                        for attempt in range(5):  # Try 5 times
                            try:
                                # Try multiple positions for send button
                                for pos_x, pos_y in send_positions:
                                    try:
                                        pyautogui.moveTo(pos_x, pos_y, duration=0.5)
                                        time.sleep(0.5)
                                        pyautogui.click()
                                        time.sleep(2)
                                        file_sent = True
                                        break
                                    except:
                                        continue
                                
                                if file_sent:
                                    break
                                    
                                # Try Enter key
                                pyautogui.press('enter')
                                time.sleep(2)
                                file_sent = True
                                break
                            except:
                                try:
                                    # Try Ctrl+Enter
                                    pyautogui.hotkey('ctrl', 'enter')
                                    time.sleep(2)
                                    file_sent = True
                                    break
                                except:
                                    try:
                                        # Try Tab and Enter
                                        pyautogui.press('tab')
                                        time.sleep(0.5)
                                        pyautogui.press('enter')
                                        time.sleep(2)
                                        file_sent = True
                                        break
                                    except:
                                        time.sleep(1)
                        
                        if not file_sent:
                            logger.error("Failed to send audio file after multiple attempts")
                        else:
                            logger.info(f"Audio file sent to {number}")
                        
                    except Exception as e:
                        logger.error(f"Failed to send audio file to {number}: {e}")
                
                logger.info(f"Alert sent to {number}")
                time.sleep(3)
                success = True
                
            except Exception as e:
                logger.error(f"Failed to send alert to {number}: {e}")
                continue
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending emergency alert: {e}")
        return False