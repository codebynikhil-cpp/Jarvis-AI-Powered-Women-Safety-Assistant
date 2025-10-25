# Jarvis AI-Powered Women Safety Assistant

A sophisticated AI-driven safety application designed to empower women with intelligent assistance, real-time threat detection, and emergency response capabilities. Built with cutting-edge machine learning and natural language processing technologies.

## 🎯 Project Overview

Jarvis is an intelligent safety assistant that combines artificial intelligence, geolocation tracking, emergency alerts, and voice assistance to provide comprehensive personal security. The system leverages advanced AI models for threat analysis, real-time monitoring, and immediate emergency response coordination.

## ✨ Key Features

- **AI-Powered Voice Assistant** - Natural language understanding and command processing
- **Real-time Audio Recording** - Automatic incident recording for evidence
- **Threat Detection System** - Machine learning-based anomaly detection
- **Emergency Alert Mechanism** - One-tap SOS with automatic contact notification
- **WhatsApp Automation** - Direct emergency alerts to contacts via WhatsApp
- **Speech Recognition** - Accurate voice command processing
- **Text-to-Speech Output** - Natural voice responses
- **Chatbot Assistant** - Intelligent conversation and guidance
- **Image Generation** - AI-powered visual content creation
- **Real-time Search Engine** - Quick information retrieval
- **Location Tracking** - GPS-based coordinate logging
- **Automation Engine** - Task automation and workflow management

## 🛠️ Tech Stack

- **Python 3.9+** - Core application framework
- **Machine Learning** - TensorFlow, scikit-learn for threat detection
- **Natural Language Processing** - NLTK, spaCy for AI assistant
- **GUI Framework** - PyQt5/PyQt6 for desktop interface
- **Speech Processing** - Google Speech-to-Text, pyttsx3 for Text-to-Speech
- **Image Generation** - DALL-E or Stable Diffusion integration
- **Automation** - Selenium for WhatsApp & browser automation
- **Audio Processing** - PyAudio for recording and playback
- **Database** - SQLite/JSON for local data storage
- **Real-time Search** - DuckDuckGo or Google API integration

## 📋 Prerequisites

Before installation, ensure you have the following installed on your system:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package manager (comes with Python)
- **Git** - [Download Git](https://git-scm.com/)
- **PortAudio** - For audio processing support
- **Virtual Environment** - Python venv or conda

### System-Specific Requirements

**Windows:**
```bash
# Install via Chocolatey (optional)
choco install python portaudio
```

**macOS:**
```bash
brew install python portaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3 python3-pip portaudio19-dev python3-pyaudio
```

## 🚀 Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/codebynikhil-cpp/Jarvis-AI-Powered-Women-Safety-Assistant.git
cd Jarvis-AI-Powered-Women-Safety-Assistant
```

### Step 2: Create Virtual Environment

**Using venv (Recommended):**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Using Conda:**
```bash
conda create -n jarvis python=3.9
conda activate jarvis
```

### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 4: Install Python Dependencies

**Install all requirements at once:**
```bash
pip install -r Requirements.txt
```

**Or install libraries individually:**

#### Core & GUI Dependencies
```bash
pip install PyQt5==5.15.9
pip install PyQt5-sip==12.13.0
pip install python-dotenv==0.21.0
```

#### Audio Processing
```bash
pip install pyaudio==0.2.13
pip install pyttsx3==2.90
pip install SpeechRecognition==3.10.0
pip install sounddevice==0.4.6
pip install soundfile==0.12.1
```

#### Machine Learning & AI
```bash
pip install tensorflow==2.13.0
pip install scikit-learn==1.3.1
pip install numpy==1.24.3
pip install scipy==1.11.2
pip install pandas==2.0.3
```

#### Natural Language Processing
```bash
pip install nltk==3.8.1
pip install spacy==3.6.1
pip install textblob==0.17.1
```

#### Google Cloud & APIs
```bash
pip install google-cloud-speech==2.21.0
pip install google-cloud-texttospeech==2.14.1
pip install google-auth==2.23.0
pip install google-api-python-client==2.97.0
```

#### Web & Search
```bash
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install selenium==4.13.0
pip install duckduckgo-search==3.9.4
```

#### Image & Media Generation
```bash
pip install pillow==10.0.0
pip install opencv-python==4.8.1
pip install matplotlib==3.7.2
pip install openai==0.28.0
```

#### Automation & Utilities
```bash
pip install pywhatkit==6.4
pip install pyautogui==0.9.53
pip install python-dateutil==2.8.2
pip install geopy==2.3.0
```

#### Additional Libraries
```bash
pip install flask==2.3.3
pip install flask-cors==4.0.0
pip install pydantic==2.3.0
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root by copying the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Google Cloud APIs
GOOGLE_SPEECH_API_KEY=your_google_speech_api_key
GOOGLE_TTS_API_KEY=your_google_tts_api_key
GOOGLE_CREDENTIALS_PATH=path/to/google-credentials.json

# OpenAI API (for image generation)
OPENAI_API_KEY=your_openai_api_key

# Emergency Contacts
EMERGENCY_PHONE_NUMBERS=+919876543210,+919876543211
EMERGENCY_EMAIL=emergency@example.com
POLICE_HELPLINE=100

# Application Settings
DEBUG_MODE=False
LOG_LEVEL=INFO
MAX_RECORDING_DURATION=300

# WhatsApp Automation
WHATSAPP_ENABLED=True
WHATSAPP_WEB_TIMEOUT=30

# Audio Settings
AUDIO_SAMPLE_RATE=44100
AUDIO_CHUNK_SIZE=1024
AUDIO_FORMAT=wav

# Search Engine
SEARCH_ENGINE=duckduckgo
MAX_SEARCH_RESULTS=5

# Location Tracking
ENABLE_GPS=True
GEOFENCE_RADIUS_METERS=1000
```

### Step 6: Download Language Models

```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"
```

### Step 7: Setup Google Cloud Credentials (Optional but Recommended)

1. Create a Google Cloud project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Speech-to-Text and Text-to-Speech APIs
3. Create a service account and download JSON credentials
4. Save as `google-credentials.json` in project root
5. Update `.env` with the path

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/google-credentials.json"
```

### Step 8: Run the Application

**Start the main application:**
```bash
python Main.py
```

**Or run individual modules:**

```bash
# Start GUI only
python Frontend/GUI.py

# Start chatbot backend
python Backend/Chatbot.py

# Test emergency detector
python Backend/EmergencyDetector.py

# Test speech recognition
python Backend/SpeechToText.py
```

## 📁 Project Structure

```
Jarvis-AI-Powered-Women-Safety-Assistant/
├── 📁 Backend/                          # Core AI & processing modules
│   ├── AudioRecorder.py                 # Audio capture and recording
│   ├── Automation.py                    # Task automation engine
│   ├── Chatbot.py                       # Main chatbot logic
│   ├── EmergencyButton.py               # Emergency trigger handler
│   ├── EmergencyDetector.py             # Threat detection AI
│   ├── ImageGeneration.py               # AI image generation
│   ├── Model.py                         # ML model definitions
│   ├── RealtimeSearchEngine.py          # Web search integration
│   ├── SpeechToText.py                  # Audio to text conversion
│   ├── TextToSpeech.py                  # Text to audio synthesis
│   ├── WhatsAppAutomation.py            # WhatsApp alert sending
│   ├── chatbotnew.py                    # Enhanced chatbot version
│   └── __init__.py                      # Package initialization
│
├── 📁 Frontend/                         # GUI & user interface
│   ├── 📁 Graphics/                     # UI icons and assets
│   │   ├── Chats.png                    # Chat interface icon
│   │   ├── Close.png                    # Window close button
│   │   ├── Home.png                     # Home screen icon
│   │   ├── Jarvis.gif                   # Animated Jarvis logo
│   │   ├── Maximize.png                 # Window maximize button
│   │   ├── Mic_off.png                  # Microphone off icon
│   │   ├── Mic_on.png                   # Microphone on icon
│   │   ├── Minimize.png                 # Window minimize button
│   │   ├── Settings.png                 # Settings icon
│   │   └── Minimize2.png                # Alternative minimize icon
│   ├── GUI.py                           # Main GUI application
│   ├── EmergencyButton.py               # Emergency UI component
│   └── tempCodeRunnerFile.py            # Temporary test file
│
├── 📁 Data/                             # Data storage & logs
│   ├── 📁 Content/                      # Content storage
│   ├── 📁 Data/                         # Processed data
│   │   └── emergency_report_*.txt       # Emergency reports
│   ├── Voice.html                       # Voice interface test
│   ├── politics.txt                     # Knowledge base sample
│   ├── ratan_tata*.jpg                  # Sample images
│   ├── speech.mp3                       # Audio sample
│   ├── speech.wav                       # Audio sample
│   └── *.txt                            # Various text data files
│
├── 📁 logs/                             # Application logs directory
│
├── 🐍 Main.py                           # Application entry point
├── 📄 Requirements.txt                  # Python dependencies
├── ⚙️ .env.example                      # Environment variables template
├── ⚙️ .gitignore                        # Git ignore rules
├── 📄 style.qss                         # Qt stylesheet (GUI styling)
├── 🎵 emergency_recording_*.wav         # Emergency audio recordings
└── 📄 README.md                         # Project documentation
```

## ⚙️ Configuration

### Requirements.txt Structure

```
PyQt5==5.15.9
PyQt5-sip==12.13.0
python-dotenv==0.21.0
pyaudio==0.2.13
pyttsx3==2.90
SpeechRecognition==3.10.0
tensorflow==2.13.0
scikit-learn==1.3.1
numpy==1.24.3
nltk==3.8.1
spacy==3.6.1
google-cloud-speech==2.21.0
google-cloud-texttospeech==2.14.1
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.13.0
duckduckgo-search==3.9.4
pillow==10.0.0
opencv-python==4.8.1
pywhatkit==6.4
pyautogui==0.9.53
```

### Quick Install from Requirements

```bash
# Install all dependencies
pip install -r Requirements.txt

# Update all packages
pip install --upgrade -r Requirements.txt

# Save current environment
pip freeze > Requirements.txt
```

## 🚀 Usage Guide

### Starting the Application

```bash
# Activate virtual environment first
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Run main application
python Main.py
```

### Using Individual Modules

**Test Speech Recognition:**
```bash
python Backend/SpeechToText.py
```

**Test Text-to-Speech:**
```bash
python Backend/TextToSpeech.py
```

**Run Emergency Detection:**
```bash
python Backend/EmergencyDetector.py
```

**Test Chatbot:**
```bash
python Backend/Chatbot.py
```

**Test Image Generation:**
```bash
python Backend/ImageGeneration.py
```

**Send WhatsApp Alert:**
```bash
python Backend/WhatsAppAutomation.py
```

## 🔧 Troubleshooting

### Common Issues

**Issue: PyAudio Installation Fails**

Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

macOS:
```bash
brew install portaudio
pip install pyaudio
```

Linux:
```bash
sudo apt-get install python3-pyaudio
# or build from source
pip install --no-cache-dir pyaudio
```

**Issue: Google API Credentials Not Found**
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# Or on Windows (Command Prompt)
set GOOGLE_APPLICATION_CREDENTIALS=path\to\credentials.json

# Or on Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\credentials.json"
```

**Issue: spaCy Model Not Found**
```bash
python -m spacy download en_core_web_sm
```

**Issue: TensorFlow/GPU Compatibility**
```bash
# CPU only version
pip install tensorflow-cpu

# GPU support (requires CUDA)
pip install tensorflow[and-cuda]
```

**Issue: PyQt5 Display Issues**

Linux:
```bash
sudo apt-get install python3-pyqt5
pip install --upgrade PyQt5
```

**Issue: Microphone Not Detected**
```bash
# Test audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# List recording devices
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(p.get_device_info_by_index(i)) for i in range(p.get_device_count())]"
```

**Issue: WhatsApp Automation Timeout**
- Ensure WhatsApp Web is responsive
- Increase timeout in `.env`: `WHATSAPP_WEB_TIMEOUT=60`
- Check internet connection stability

## 📊 Audio Configuration

Edit audio settings in `.env`:

```env
# Recording Settings
AUDIO_SAMPLE_RATE=44100        # Hz (44.1kHz or 48kHz recommended)
AUDIO_CHUNK_SIZE=1024          # Samples per chunk
AUDIO_FORMAT=wav               # File format (wav or mp3)
AUDIO_CHANNELS=1               # Mono (1) or Stereo (2)
AUDIO_BITRATE=128              # kbps for MP3
```

## 🔐 Security Best Practices

- Never commit `.env` file to version control
- Keep API keys in `.env` file only
- Rotate credentials regularly
- Use service accounts for Google APIs
- Enable two-factor authentication on accounts
- Review logs regularly for suspicious activity
- Keep all dependencies updated

Update dependencies:
```bash
pip install --upgrade pip
pip list --outdated
pip install --upgrade [package-name]
```

## 🧪 Testing

Create a test file to verify setup:

```bash
# Create test_setup.py
cat > test_setup.py << 'EOF'
import sys

print("Python version:", sys.version)

# Test imports
try:
    import PyQt5
    print("✓ PyQt5 installed")
except ImportError:
    print("✗ PyQt5 missing")

try:
    import speech_recognition
    print("✓ SpeechRecognition installed")
except ImportError:
    print("✗ SpeechRecognition missing")

try:
    import pyttsx3
    print("✓ pyttsx3 installed")
except ImportError:
    print("✗ pyttsx3 missing")

try:
    import tensorflow
    print("✓ TensorFlow installed")
except ImportError:
    print("✗ TensorFlow missing")

try:
    import spacy
    print("✓ spaCy installed")
except ImportError:
    print("✗ spaCy missing")

print("\nSetup verification complete!")
EOF

python test_setup.py
```

## 🤝 Contributing

Contributions are welcome! Follow these steps:

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Jarvis-AI-Powered-Women-Safety-Assistant.git
cd Jarvis-AI-Powered-Women-Safety-Assistant

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Make your changes
# Edit files as needed

# 5. Commit changes
git add .
git commit -m "Add your descriptive commit message"

# 6. Push to your branch
git push origin feature/your-feature-name

# 7. Submit a Pull Request on GitHub
```

## 📝 Development Workflow

```bash
# Install development tools
pip install black flake8 pylint mypy

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy Backend/
```

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support & Contact

**Author:** Nikhil  
**GitHub:** [@codebynikhil-cpp](https://github.com/codebynikhil-cpp)

For bug reports, feature requests, or general inquiries:
- Open an issue on GitHub
- Check the documentation
- Review existing issues and discussions

## ⚠️ Disclaimer

This application is designed for personal safety and emergency assistance. While it provides comprehensive safety features, it should not be considered a substitute for professional emergency services. Always contact official emergency services (Police: 100, Fire: 101) for immediate assistance.

## 📞 Emergency Resources

- **Police Helpline:** 100
- **Fire Emergency:** 101
- **Ambulance:** 102
- **Women Helpline (India):** 1091
- **Cyber Helpline (India):** 1930

---

**Made with ❤️ for Women's Safety by Nikhil**

*Last Updated: October 2025*
*Version: 1.0.0*
