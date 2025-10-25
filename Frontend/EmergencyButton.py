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
import soundfile as sf
import pyaudio
import wave
import speech_recognition as sr
from Backend.WhatsAppAutomation import send_emergency_alert
from Backend.AudioRecorder import stop_recording
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

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

# Emergency keywords
EMERGENCY_KEYWORDS = ["help", "save", "emergency", "danger", "scared", "unsafe"]

# Create emergency directory if it doesn't exist
emergency_dir = os.path.join("Data", "Emergency")
os.makedirs(emergency_dir, exist_ok=True)

class EmergencyButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("EMERGENCY", parent)
        self.setCheckable(True)
        self.clicked.connect(self.toggle_emergency)
        self.emergency_active = False
        self.emergency_detector = EmergencyDetector()
        
    def toggle_emergency(self):
        """Toggle emergency mode on/off"""
        self.emergency_active = not self.emergency_active
        if self.emergency_active:
            self.setText("MONITORING")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #ff0000;
                    color: white;
                    border: none;
                    padding: 15px;
                    font-size: 20px;
                    border-radius: 10px;
                    min-width: 200px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
            if self.emergency_detector.start_detection():
                logger.info("Emergency detection started successfully")
            else:
                logger.error("Failed to start emergency detection")
                self.emergency_active = False
                self.setChecked(False)
                self.setText("EMERGENCY")
        else:
            self.setText("EMERGENCY")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444;
                    color: white;
                    border: none;
                    padding: 15px;
                    font-size: 20px;
                    border-radius: 10px;
                    min-width: 200px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
            if self.emergency_detector.stop_detection():
                logger.info("Emergency detection stopped successfully")
            else:
                logger.error("Failed to stop emergency detection")
                self.emergency_active = True
                self.setChecked(True)
                self.setText("MONITORING")

class EmergencyDetector:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.sample_rate = 44100
        self.channels = 2
        self.threshold = 0.1
        self.voice_detection_count = 0
        self.last_alert_time = 0
        self.recognizer = sr.Recognizer()
        
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
            with sr.Microphone() as source:
                logger.info("Adjusting for ambient noise... Please wait...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                logger.info("Ready!")
                
                while self.monitoring:
                    try:
                        logger.info("Listening...")
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        
                        try:
                            # Convert speech to text
                            text = self.recognizer.recognize_google(audio).lower()
                            logger.info(f"Recognized: {text}")
                            
                            # Check for emergency keywords
                            if any(keyword in text for keyword in EMERGENCY_KEYWORDS):
                                logger.info("Emergency keyword detected!")
                                self._handle_distress()
                                
                        except sr.UnknownValueError:
                            logger.debug("Could not understand audio")
                        except sr.RequestError as e:
                            logger.error(f"Could not request results; {e}")
                            
                    except Exception as e:
                        logger.error(f"Error in audio processing: {e}")
                        time.sleep(0.1)
                        
        except Exception as e:
            logger.error(f"Error in audio monitoring: {e}")
            self.monitoring = False
    
    def _handle_distress(self):
        """Handle detected distress signal"""
        try:
            current_time = time.time()
            if current_time - self.last_alert_time < ALERT_COOLDOWN:
                logger.info("Alert cooldown in effect, skipping...")
                return
                
            # Get current location
            location = get_location()
            if not location:
                logger.error("Could not get location!")
                return
            
            # Record emergency audio
            audio_file = self._record_emergency_audio()
            if not audio_file:
                logger.error("Failed to record emergency audio")
                return
            
            # Send emergency alert
            if send_emergency_alert(location=location, audio_file=audio_file):
                logger.info("Emergency alert sent successfully")
                self.last_alert_time = current_time
            else:
                logger.error("Failed to send emergency alert")
            
        except Exception as e:
            logger.error(f"Error handling distress: {e}")
    
    def _record_emergency_audio(self, duration=10):
        """Record audio for specified duration"""
        try:
            logger.info("Recording emergency audio...")
            
            # Initialize recording
            recording = sd.rec(int(duration * self.sample_rate), 
                             samplerate=self.sample_rate, 
                             channels=self.channels,
                             dtype='float32')
            
            # Wait for recording to complete
            sd.wait()
            
            # Save recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emergency_audio_{timestamp}.wav"
            filepath = os.path.join(emergency_dir, filename)
            
            # Save as WAV file
            sf.write(filepath, recording, self.sample_rate)
            logger.info(f"Emergency audio saved to: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
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
    """Start emergency detection"""
    return emergency_detector.start_detection()

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
        
        if volume > VOLUME_THRESHOLD:
            # Frequency analysis
            fft_data = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data)) * sample_rate
            high_freq_energy = np.abs(fft_data[freqs > FREQUENCY_THRESHOLD]).mean()
            
            logger.info(f"High frequency energy: {high_freq_energy}")
            
            if high_freq_energy > VOLUME_THRESHOLD:
                logger.info("Distress signal detected!")
                return True
    except Exception as e:
        logger.error(f"Error in distress detection: {e}")
    return False

def monitor_audio():
    """Monitor audio for emergency signals."""
    global recording, emergency_active
    last_alert_time = 0
    
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
                    current_time = time.time()
                    if current_time - last_alert_time >= ALERT_COOLDOWN:
                        logger.info("Distress signal detected!")
                        
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
                        if send_emergency_alert(location, audio_file):
                            logger.info("Emergency alert sent successfully")
                            last_alert_time = current_time
                        else:
                            logger.error("Failed to send emergency alert")
                
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