import speech_recognition as sr
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")

# Helper path setup
current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    if any(new_query.startswith(word) for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise... Please wait...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready!")

    def recognize(self):
        try:
            print("\nListening... Speak now!")
            SetAssistantStatus("Listening...")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            print("Processing speech...")
            SetAssistantStatus("Processing...")
            
            try:
                text = self.recognizer.recognize_google(audio, language=InputLanguage)
                print(f"Recognized: {text}")
                
                if "en" in InputLanguage.lower():
                    return QueryModifier(text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(text))
                    
            except sr.UnknownValueError:
                print("Could not understand audio")
                SetAssistantStatus("Could not understand audio. Please try again.")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                SetAssistantStatus("Error accessing speech recognition service. Please check your internet connection.")
                return None
                
        except Exception as e:
            print(f"Error in speech recognition: {str(e)}")
            SetAssistantStatus("Error in speech recognition. Please try again.")
            return None

# Create a global instance
recognizer = SpeechRecognizer()

def SpeechRecognition():
    return recognizer.recognize()

# Main loop for testing
if __name__ == "__main__":
    try:
        while True:
            print("\nPress Enter to start speaking (or Ctrl+C to exit)...")
            input()
            Text = SpeechRecognition()
            if Text:
                print("Final text:", Text)
    except KeyboardInterrupt:
        print("\nExiting...")


