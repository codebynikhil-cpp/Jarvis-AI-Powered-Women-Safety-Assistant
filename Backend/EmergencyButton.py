import os
import sys

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

from Backend.EmergencyDetector import start_detection, stop_recording
import threading
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Global variables
emergency_thread = None
emergency_active = False

def toggle_emergency_mode():
    """
    Toggle the emergency detection system on/off.
    Returns True if the system was successfully toggled.
    """
    global emergency_thread, emergency_active
    
    try:
        if not emergency_active:
            # Start emergency detection
            if start_detection():
                emergency_active = True
                logger.info("Emergency detection system activated")
                return True
        else:
            # Stop emergency detection
            if stop_recording():
                emergency_active = False
                logger.info("Emergency detection system deactivated")
                return True
                
        return False
    except Exception as e:
        logger.error(f"Error toggling emergency mode: {e}")
        return False

def get_emergency_status():
    """
    Get the current status of the emergency detection system.
    Returns True if the system is active.
    """
    global emergency_active
    return emergency_active 