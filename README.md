# Jarvis AI-Powered Women Safety Assistant

A sophisticated AI-driven safety application designed to empower women with intelligent assistance, real-time threat detection, and emergency response capabilities. Built with cutting-edge machine learning and natural language processing technologies.

## 🎯 Project Overview

Jarvis is an intelligent safety assistant that combines artificial intelligence, geolocation tracking, emergency alerts, and voice assistance to provide comprehensive personal security. The system leverages advanced AI models for threat analysis, real-time monitoring, and immediate emergency response coordination.

## ✨ Key Features

- **AI-Powered Voice Assistant** - Natural language understanding and command processing
- **Real-time Location Tracking** - GPS integration for emergency responders
- **Threat Detection System** - Machine learning-based anomaly detection
- **Emergency Alert Mechanism** - One-tap SOS with automatic contact notification
- **Geofencing Alerts** - Safe zone monitoring and boundary alerts
- **Incident Reporting** - Automated report generation and logging
- **Community Safety Network** - Connect with nearby users for collective safety
- **Audio/Video Recording** - Evidence capture for safety documentation
- **Integration with Emergency Services** - Direct coordination with authorities

## 🛠️ Tech Stack

- **Python 3.9+** - Core application framework
- **Machine Learning** - TensorFlow, scikit-learn for threat detection
- **Natural Language Processing** - NLTK, spaCy for AI assistant
- **Backend** - Flask/Django for API services
- **Database** - MongoDB/PostgreSQL for data persistence
- **Frontend** - React.js or Vue.js for user interface
- **Geolocation** - Google Maps API, OpenStreetMap
- **Real-time Communication** - WebSockets, Firebase
- **Voice Processing** - Google Speech-to-Text, Text-to-Speech APIs

## 📋 Prerequisites

Before installation, ensure you have the following installed on your system:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package manager (comes with Python)
- **Git** - [Download Git](https://git-scm.com/)
- **Node.js 14+** (if frontend included) - [Download Node.js](https://nodejs.org/)
- **MongoDB** or **PostgreSQL** - Database systems
- **Virtual Environment** - Python venv or conda

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
pip install -r requirements.txt
```

**Or install libraries individually:**

#### Core Dependencies
```bash
pip install python-dotenv==0.19.0
pip install pyaudio==0.2.11
```

#### Machine Learning & AI Libraries
```bash
pip install tensorflow==2.12.0
pip install scikit-learn==1.3.0
pip install numpy==1.24.3
pip install scipy==1.11.0
pip install pandas==2.0.3
```

#### Natural Language Processing
```bash
pip install nltk==3.8.1
pip install spacy==3.6.0
pip install textblob==0.17.1
```

#### Backend Framework
```bash
pip install flask==2.3.2
pip install flask-cors==4.0.0
pip install flask-restx==0.5.1
```

#### Database Drivers
```bash
pip install pymongo==4.4.0
pip install psycopg2-binary==2.9.6
pip install sqlalchemy==2.0.19
```

#### Geolocation & Maps
```bash
pip install geopy==2.3.0
pip install googlemaps==4.10.0
```

#### Real-time Communication
```bash
pip install python-socketio==5.9.0
pip install python-engineio==4.7.1
pip install firebase-admin==6.2.0
```

#### Voice & Audio Processing
```bash
pip install google-cloud-speech==2.21.0
pip install google-cloud-texttospeech==2.14.0
pip install SpeechRecognition==3.10.0
pip install pyttsx3==2.90
```

#### Additional Utilities
```bash
pip install requests==2.31.0
pip install python-dateutil==2.8.2
pip install pillow==10.0.0
pip install opencv-python==4.8.0
```

### Step 5: Install Frontend Dependencies (if applicable)

```bash
cd frontend
npm install
cd ..
```

### Step 6: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_SPEECH_API_KEY=your_google_speech_api_key
FIREBASE_API_KEY=your_firebase_api_key

# Database Configuration
DATABASE_URL=mongodb://localhost:27017/jarvis
# or
DATABASE_URL=postgresql://user:password@localhost:5432/jarvis

# Server Configuration
FLASK_ENV=development
FLASK_PORT=5000
DEBUG=True

# Emergency Contacts
EMERGENCY_CONTACT_NUMBER=1234567890
POLICE_HELPLINE=911

# Location Services
ENABLE_GPS_TRACKING=True
GEOFENCE_RADIUS_KM=1

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### Step 7: Download NLP Models

```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

### Step 8: Initialize Database

```bash
# For MongoDB
python scripts/init_db.py

# For PostgreSQL (if using Flask-Migrate)
flask db init
flask db migrate
flask db upgrade
```

### Step 9: Run the Application

**Backend Server:**
```bash
python app.py
# or
flask run
```

**Frontend (if applicable):**
```bash
cd frontend
npm start
cd ..
```

The application will be available at `http://localhost:5000`

## 📦 Generate Requirements File

To create a requirements.txt from your environment:

```bash
pip freeze > requirements.txt
```

To update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

## 🔧 Troubleshooting

### Common Issues

**Issue: PyAudio installation fails**
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install python3-pyaudio
```

**Issue: TensorFlow compatibility**
```bash
# For GPU support
pip install tensorflow[and-cuda]

# For CPU only
pip install tensorflow-cpu
```

**Issue: Spacy model not found**
```bash
python -m spacy download en_core_web_sm
```

**Issue: Google API keys not recognized**
- Verify .env file is in project root
- Reload the application after updating .env
- Check API key validity in Google Cloud Console

## 📁 Project Structure

```
Jarvis-AI-Powered-Women-Safety-Assistant/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── config/
│   ├── settings.py            # Configuration settings
│   └── database.py            # Database configuration
├── models/
│   ├── threat_detection.py    # ML threat detection model
│   ├── ai_assistant.py        # AI assistant logic
│   └── user.py                # User database models
├── routes/
│   ├── auth.py                # Authentication routes
│   ├── emergency.py           # Emergency response routes
│   ├── tracking.py            # Location tracking routes
│   └── assistant.py           # AI assistant routes
├── services/
│   ├── voice_service.py       # Voice processing service
│   ├── location_service.py    # Geolocation service
│   ├── notification_service.py # Alert notifications
│   └── email_service.py       # Email notifications
├── utils/
│   ├── helpers.py             # Utility functions
│   └── validators.py          # Input validation
├── frontend/                  # React/Vue frontend
│   ├── public/
│   ├── src/
│   └── package.json
├── tests/
│   ├── test_models.py         # Model tests
│   └── test_routes.py         # Route tests
├── scripts/
│   ├── init_db.py             # Database initialization
│   └── seed_data.py           # Sample data seeding
└── README.md                  # Project documentation
```

## 🧪 Running Tests

```bash
# Install testing framework
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=.
```

## 🐳 Docker Deployment (Optional)

**Build Docker image:**
```bash
docker build -t jarvis-ai .
```

**Run Docker container:**
```bash
docker run -p 5000:5000 --env-file .env jarvis-ai
```

## 🔐 Security Best Practices

- Never commit `.env` files to version control
- Use strong API keys and rotate regularly
- Implement rate limiting on API endpoints
- Enable HTTPS in production
- Validate all user inputs
- Keep dependencies updated: `pip list --outdated`
- Use environment-specific configurations

## 📚 API Documentation

API documentation is available at:
```
http://localhost:5000/api/docs
```

Alternatively, check the `/docs` folder for detailed API specifications.

## 🤝 Contributing

Contributions are welcome! Follow these steps:

1. **Fork the repository**
   ```bash
   # Click 'Fork' on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Jarvis-AI-Powered-Women-Safety-Assistant.git
   cd Jarvis-AI-Powered-Women-Safety-Assistant
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes and commit**
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

5. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a Pull Request**
   - Go to GitHub and open a Pull Request
   - Describe your changes in detail
   - Link any related issues

## 📋 Development Workflow

**Install development dependencies:**
```bash
pip install -r requirements-dev.txt
```

**Code formatting:**
```bash
black .
flake8 .
```

**Type checking:**
```bash
mypy .
```

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support & Contact

**Author:** Nikhil  
**GitHub:** [@codebynikhil-cpp](https://github.com/codebynikhil-cpp)  

For bug reports, feature requests, or general inquiries:
- Open an issue on GitHub
- Contact the development team
- Check existing documentation

## ⚠️ Disclaimer

This application is designed for personal safety and emergency assistance. While it provides comprehensive safety features, it should not be considered a substitute for professional emergency services. Always contact official emergency services for immediate assistance.

---

**Made with ❤️ for Women's Safety by Nikhil**

*Last Updated: October 2025*
