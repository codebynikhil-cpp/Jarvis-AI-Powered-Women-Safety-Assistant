import os
import sys
import numpy as np
import geocoder
import threading
import time
from datetime import datetime
import wave
import logging
import sounddevice as sd
import pyaudio
import wave
from Backend.WhatsAppAutomation import send_emergency_alert
from Backend.AudioRecorder import stop_recording

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Global variables
recording = False
audio_thread = None
emergency_active = False
VOLUME_THRESHOLD = 0.1
FREQUENCY_THRESHOLD = 1000
ALERT_COOLDOWN = 60  # 60 seconds cooldown between alerts

class EmergencyDetector:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.sample_rate = 44100
        self.channels = 2
        self.threshold = 0.5  # Volume threshold for distress detection
        
    def start_detection(self):
        """Start monitoring for distress signals"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_audio)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Emergency detection started")
            return True
        return False
    
    def _monitor_audio(self):
        """Monitor audio input for distress signals"""
        try:
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Monitoring status: {status}")
                if self.monitoring:
                    # Calculate volume level
                    volume = np.abs(indata).mean()
                    if volume > self.threshold:
                        logger.info(f"Distress signal detected! Volume: {volume}")
                        self._handle_distress()
            
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=callback):
                logger.info("Monitoring audio...")
                while self.monitoring:
                    sd.sleep(100)  # Sleep for 100ms
                    
        except Exception as e:
            logger.error(f"Error in audio monitoring: {e}")
    
    def _handle_distress(self):
        """Handle detected distress signal"""
        try:
            # Stop monitoring
            self.monitoring = False
            
            # Get the recorded audio file
            audio_file = stop_recording()
            if not audio_file:
                logger.error("Failed to get audio file")
                return
            
            # Send emergency alert with audio file
            send_emergency_alert(audio_file=audio_file)
            
        except Exception as e:
            logger.error(f"Error handling distress: {e}")
    
    def stop_detection(self):
        """Stop monitoring for distress signals"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("Emergency detection stopped")
            return True
        return False

# Create a global instance
emergency_detector = EmergencyDetector()

def start_detection():
    """Start the emergency detection system."""
    global recording, audio_thread, emergency_active
    
    try:
        if not emergency_active:
            recording = True
            audio_thread = threading.Thread(target=monitor_audio)
            audio_thread.daemon = True
            audio_thread.start()
            emergency_active = True
            logger.info("Emergency detection system activated")
            return True
        return False
    except Exception as e:
        logger.error(f"Error starting detection: {e}")
        return False

def stop_detection():
    """Stop emergency detection"""
    return emergency_detector.stop_detection()

def get_location():
    """Get current location using geocoder."""
    try:
        g = geocoder.ip('me')
        return {
            'address': g.address,
            'coordinates': (g.lat, g.lng)
        }
    except Exception as e:
        logger.error(f"Error getting location: {e}")
        return None

def detect_distress(audio_data, sample_rate):
    """Analyze audio data for distress signals."""
    try:
        # Volume analysis
        volume = np.abs(audio_data).mean()
        logger.info(f"Current volume level: {volume}")
        
        # Lower threshold for initial detection
        if volume > 0.01:  # Lowered threshold for initial voice detection
            # Frequency analysis
            fft_data = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data)) * sample_rate
            high_freq_energy = np.abs(fft_data[freqs > FREQUENCY_THRESHOLD]).mean()
            
            logger.info(f"High frequency energy: {high_freq_energy}")
            
            # Check for sustained voice activity
            if high_freq_energy > 0.005:  # Lowered threshold for frequency analysis
                logger.info("Voice activity detected!")
                return True
    except Exception as e:
        logger.error(f"Error in distress detection: {e}")
    return False

def get_audio_file():
    """Get the latest recorded audio file"""
    try:
        emergency_dir = os.path.join("Data", "Emergency")
        if not os.path.exists(emergency_dir):
            return None
            
        # Get the most recent audio file
        audio_files = [f for f in os.listdir(emergency_dir) if f.endswith('.wav')]
        if not audio_files:
            return None
            
        latest_file = max(audio_files, key=lambda x: os.path.getctime(os.path.join(emergency_dir, x)))
        return os.path.join(emergency_dir, latest_file)
    except Exception as e:
        logger.error(f"Error getting audio file: {e}")
        return None

def monitor_audio():
    """Monitor audio for emergency signals."""
    global recording, emergency_active
    last_alert_time = 0
    voice_detection_count = 0  # Counter for sustained voice detection
    
    try:
        # Audio monitoring parameters
        sample_rate = 44100
        channels = 2
        dtype = np.int16
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        logger.info("Started monitoring...")
        
        while recording:
            try:
                # Read audio data
                audio_data = np.frombuffer(stream.read(1024), dtype=np.int16)
                
                # Convert to float for processing
                audio_float = audio_data.astype(np.float32) / 32768.0
                
                # Check for emergency conditions
                if detect_distress(audio_float, sample_rate):
                    voice_detection_count += 1
                    logger.info(f"Voice detection count: {voice_detection_count}")
                    
                    # If we detect sustained voice activity (3 consecutive detections)
                    if voice_detection_count >= 3:
                        current_time = time.time()
                        if current_time - last_alert_time >= ALERT_COOLDOWN:
                            logger.info("Sustained voice activity detected - triggering emergency alert!")
                            
                            # Get current location
                            location = get_location()
                            if not location:
                                logger.error("Could not get location!")
                                continue
                            
                            # Get the recorded audio file
                            audio_file = get_audio_file()
                            if not audio_file:
                                logger.error("Could not get audio file!")
                                continue
                            
                            # Send emergency alert
                            if send_emergency_alert(location=location, audio_file=audio_file):
                                logger.info("Emergency alert sent successfully")
                                last_alert_time = current_time
                            else:
                                logger.error("Failed to send emergency alert")
                else:
                    voice_detection_count = 0  # Reset counter if no voice detected
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                time.sleep(0.1)
            
    except Exception as e:
        logger.error(f"Error in audio monitoring: {e}")
    finally:
        recording = False
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        if 'p' in locals():
            p.terminate()

def stop_recording():
    """Stop the emergency detection system."""
    global recording, audio_thread, emergency_active
    
    try:
        if emergency_active:
            recording = False
            if audio_thread and audio_thread.is_alive():
                audio_thread.join(timeout=5)
            emergency_active = False
            logger.info("Emergency detection system deactivated")
            return True
        return False
    except Exception as e:
        logger.error(f"Error stopping recording: {e}")
        return False 