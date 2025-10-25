from groq import Groq
import cohere
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
CohereAPIKey = env_vars.get("COHERE_API_KEY")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)
# Initialize Cohere client as fallback
cohere_client = cohere.Client(api_key=CohereAPIKey)

# Chatbot system message
System = f"""You are JARVIS AI. Only introduce yourself when directly asked about who you are or what you can do.
*** Key Instructions ***
- Answer questions directly without unnecessary introductions
- Only mention being "Nikhil's AI assistant" when asked about your identity
- Reply in English even for non-English questions
- Focus on the task or question at hand
- Keep responses concise and relevant
"""

# Update SYSTEM_PROMPT to be more focused
SYSTEM_PROMPT = """Maintain professional and helpful responses.
Only introduce yourself when specifically asked.
Focus on answering questions and completing tasks efficiently."""

# System chatbot context
SystemChatBot = [{"role": "system", "content": System}]

# Load chat history or create a new file if it doesn't exist
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f)

# Cache for real-time information
_real_time_cache = {"data": None, "timestamp": 0}

# Function to get real-time information
def RealtimeInformation():
    global _real_time_cache
    current_time = datetime.datetime.now().timestamp()

    # Cache real-time information for 60 seconds
    if _real_time_cache["data"] and (current_time - _real_time_cache["timestamp"] < 60):
        return _real_time_cache["data"]

    now = datetime.datetime.now()
    data = (
        f"Please use this real time information if needed,\n"
        f"Day: {now.strftime('%A')}\nDate: {now.strftime('%d')}\nMonth: {now.strftime('%B')}\nYear: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours :{now.strftime('%M')} minutes :{now.strftime('%S')} seconds.\n"
    )
    _real_time_cache = {"data": data, "timestamp": current_time}
    return data

# Function to clean up the answer
def AnswerModifier(Answer):
    return '\n'.join([line for line in Answer.split('\n') if line.strip()])

class Chatbot:
    def __init__(self):
        self.messages = messages
        self.client = client

    def chat(self, query):
        try:
            # Check if query is asking about identity
            identity_keywords = [
                "who are you",
                "what are you",
                "introduce yourself",
                "tell me about yourself",
                "what can you do",
                "your name",
                "who made you"
            ]
            
            is_identity_question = any(keyword in query.lower() for keyword in identity_keywords)
            
            # Add context only for identity questions
            current_context = SystemChatBot
            if is_identity_question:
                introduction = {
                    "role": "system",
                    "content": "You are JARVIS AI, an advanced artificial intelligence assistant created by Nikhil."
                }
                current_context = SystemChatBot + [introduction]

            # Append user query
            self.messages.append({"role": "user", "content": query})

            # Try Groq first, fallback to Cohere if it fails
            try:
                # Generate response with Groq
                completion = self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=current_context + [{"role": "system", "content": RealtimeInformation()}] + self.messages[-5:],
                    max_tokens=1024,
                    temperature=0.7,
                    top_p=1,
                    stream=True,
                    stop=None
                )

                Answer = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        Answer += chunk.choices[0].delta.content

            except Exception as groq_error:
                print(f"Groq API failed: {groq_error}")
                # Fallback to Cohere
                try:
                    # Prepare messages for Cohere
                    cohere_messages = []
                    for msg in current_context + [{"role": "system", "content": RealtimeInformation()}] + self.messages[-5:]:
                        if msg["role"] == "user":
                            cohere_messages.append({"role": "user", "message": msg["content"]})
                        elif msg["role"] == "assistant":
                            cohere_messages.append({"role": "assistant", "message": msg["content"]})
                        elif msg["role"] == "system":
                            cohere_messages.append({"role": "system", "message": msg["content"]})
                    
                    # Generate response with Cohere
                    response = cohere_client.chat(
                        model="command-r-plus",
                        message=query,
                        preamble=System,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    Answer = response.text

                except Exception as cohere_error:
                    print(f"Cohere API also failed: {cohere_error}")
                    Answer = "I apologize, but both AI services are currently unavailable. Please try again later."

            # Clean and save the assistant's response
            Answer = Answer.replace("</s>", "")
            self.messages.append({"role": "assistant", "content": Answer})

            # Save updated chat history
            with open(r"Data\ChatLog.json", "w") as f:
                dump(self.messages, f, indent=4)

            return AnswerModifier(Answer=Answer)

        except Exception as e:
            print(f"Error in Chatbot.chat: {e}")
            return "I apologize, but I encountered an error. Please try again."

# Main script execution
if __name__ == "__main__":
    chatbot = Chatbot()
    while True:
        user_input = input("Enter Your Question: ")
        print(chatbot.chat(user_input))