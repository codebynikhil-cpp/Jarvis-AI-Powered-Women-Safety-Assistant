import os
import sys
import json
import logging
from typing import List, Dict, Any
import datetime
from dotenv import load_dotenv

# Suppress logging for production
logging.getLogger().setLevel(logging.CRITICAL)

# Attempt to import Groq, with graceful handling
try:
    from groq import Groq
except ImportError:
    sys.exit(1)

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class ChatbotConfig:
    """Manages configuration and environment variables."""
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Ensure Data directory exists
        self.data_dir = "Data"
        os.makedirs(self.data_dir, exist_ok=True)

        # Chat history file path
        self.chat_log_path = os.path.join(self.data_dir, "ChatLog.json")

        # Load and validate configuration
        self.config = self._load_configuration()

    def _load_configuration(self) -> Dict[str, str]:
        """
        Load and validate configuration from environment variables.
        
        Returns:
            Dict of configuration values.
        """
        config = {}
        
        # Mapping of possible environment variable names
        var_mappings = {
            "Username": ["USERNAME", "User"],
            "Assistantname": ["ASSISTANT_NAME", "ASSISTANTNAME", "Assistantname"],
            "GroqAPIKey": ["GROQ_API_KEY", "GroqAPIKey"]
        }
        
        for config_key, possible_keys in var_mappings.items():
            value = None
            
            # Try each possible key
            for key in possible_keys:
                value = os.getenv(key)
                if value:
                    break
            
            # Special handling for API Key
            if config_key == "GroqAPIKey":
                if not value:
                    sys.exit(1)
            
            # Default values for other keys
            if not value:
                if config_key == "Username":
                    value = "User"
                elif config_key == "Assistantname":
                    value = "Jarvis"
            
            config[config_key] = value
        
        return config

class ChatHistoryManager:
    """Manages chat history with file persistence."""
    def __init__(self, file_path: str, max_history: int = 50):
        """
        Initialize ChatHistoryManager.
        
        Args:
            file_path (str): Path to chat history JSON file.
            max_history (int): Maximum number of messages to keep.
        """
        self.file_path = file_path
        self.max_history = max_history
        self.messages: List[Dict[str, str]] = self._load_history()

    def _load_history(self) -> List[Dict[str, str]]:
        """
        Load chat history from file.
        
        Returns:
            List of message dictionaries.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to chat history.
        
        Args:
            role (str): Message role (user/assistant).
            content (str): Message content.
        """
        self.messages.append({"role": role, "content": content})
        
        # Trim history if it exceeds max_history
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        
        self._save_history()

    def _save_history(self) -> None:
        """Save chat history to file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def get_recent_context(self, num_messages: int = 5) -> List[Dict[str, str]]:
        """
        Get recent context for chat completion.
        
        Args:
            num_messages (int): Number of recent messages to retrieve.
        
        Returns:
            List of recent message dictionaries.
        """
        return self.messages[-num_messages:]

class GroqChatbot:
    """Primary chatbot class using Groq API."""
    def __init__(self):
        """Initialize chatbot with configuration and services."""
        try:
            # Load configuration
            self.config = ChatbotConfig()

            # Initialize Groq client
            self.client = Groq(api_key=self.config.config["GroqAPIKey"])

            # Initialize history manager
            self.history_manager = ChatHistoryManager(self.config.chat_log_path)

            # Define system message
            self.system_message = {
                "role": "system", 
                "content": f"""You are {self.config.config['Assistantname']}, an advanced AI assistant created to help {self.config.config['Username']}.

Communication Guidelines:
- Provide concise, accurate, and helpful responses
- Use English for all communications
- Focus on directly answering the question
- Maintain context from previous interactions
- Prioritize clarity and precision
- Address {self.config.config['Username']} directly and personally"""
            }

        except Exception:
            sys.exit(1)

    def _sanitize_response(self, response: str) -> str:
        """
        Sanitize and clean the AI's response.
        
        Args:
            response (str): Raw response from AI.
        
        Returns:
            str: Cleaned response.
        """
        # Remove system tokens, extra whitespaces
        cleaned_response = response.replace("</s>", "").strip()
        
        # Remove consecutive blank lines
        lines = [line for line in cleaned_response.split('\n') if line.strip()]
        return '\n'.join(lines)

    def chat(self, query: str) -> str:
        """
        Generate a chat response.
        
        Args:
            query (str): User's input query.
        
        Returns:
            str: AI's response.
        """
        try:
            # Prepare messages for API call
            messages = [
                self.system_message,
                {"role": "system", "content": f"Current date and time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
            ] + self.history_manager.get_recent_context()

            # Add current user message
            messages.append({"role": "user", "content": query})

            # Generate response using Groq API
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            # Collect streamed response
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content

            # Sanitize and process response
            cleaned_response = self._sanitize_response(response)

            # Update chat history
            self.history_manager.add_message("user", query)
            self.history_manager.add_message("assistant", cleaned_response)

            return cleaned_response

        except Exception:
            return "I apologize, but I'm having trouble processing your request right now."

def main():
    """Main function to run the chatbot."""
    try:
        chatbot = GroqChatbot()
        
        while True:
            try:
                user_input = input(f"{chatbot.config.config['Username']}: ")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye!")
                    break
                
                response = chatbot.chat(user_input)
                print(f"{chatbot.config.config['Assistantname']}: {response}\n")
            
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
    
    except Exception:
        print("An error occurred during initialization.")

if __name__ == "__main__":
    main()