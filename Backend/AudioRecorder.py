import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_thread = None
        self.recording_data = []
        self.sample_rate = 44100
        self.channels = 2
        
    def start_recording(self):
        """Start recording audio"""
        if not self.recording:
            self.recording = True
            self.recording_data = []
            
            # Start recording in a separate thread
            self.audio_thread = threading.Thread(target=self._record)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            logger.info("Audio recording started")
            return True
        return False
    
    def _record(self):
        """Internal recording function"""
        try:
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Recording status: {status}")
                if self.recording:
                    self.recording_data.append(indata.copy())
            
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=callback):
                logger.info("Recording...")
                while self.recording:
                    sd.sleep(100)  # Sleep for 100ms
                
        except Exception as e:
            logger.error(f"Error in recording: {e}")
    
    def stop_recording(self):
        """Stop recording and save the audio file"""
        if self.recording:
            self.recording = False
            if self.audio_thread:
                self.audio_thread.join(timeout=5)
            
            if self.recording_data:
                try:
                    # Create Emergency directory if it doesn't exist
                    os.makedirs("Data/Emergency", exist_ok=True)
                    
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"Data/Emergency/emergency_recording_{timestamp}.wav"
                    
                    # Combine all recorded data
                    recording = np.concatenate(self.recording_data, axis=0)
                    
                    # Save the recording
                    sf.write(filename, recording, self.sample_rate)
                    
                    logger.info(f"Audio saved to {filename}")
                    
                    # Verify the file exists and has content
                    if os.path.exists(filename) and os.path.getsize(filename) > 0:
                        return filename
                    else:
                        logger.error("Audio file was not created properly")
                        return None
                        
                except Exception as e:
                    logger.error(f"Error saving audio file: {e}")
                    return None
            
            logger.info("Recording stopped")
            return None
        return None
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_recording()

# Create a global instance
audio_recorder = AudioRecorder()

def start_recording():
    """Start recording audio"""
    return audio_recorder.start_recording()

def stop_recording():
    """Stop recording and get the audio file path"""
    return audio_recorder.stop_recording()

def cleanup():
    """Clean up resources"""
    audio_recorder.cleanup() 