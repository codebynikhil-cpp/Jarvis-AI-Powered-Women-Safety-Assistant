from googlesearch import search
from groq import Groq
import cohere
import json
import os
from dotenv import dotenv_values
import time
import threading
import concurrent.futures
import requests
from bs4 import BeautifulSoup

# Load environment variables
env_vars = dotenv_values(".env")
ASSISTANTNAME = env_vars.get("Assistantname", "JARVIS")
GroqApiKey = env_vars.get("GROQ_API_KEY")
CohereApiKey = env_vars.get("COHERE_API_KEY")

# Initialize Groq client
client = Groq(api_key=GroqApiKey)
# Initialize Cohere client as fallback
cohere_client = cohere.Client(api_key=CohereApiKey)

# Constants
SYSTEM_PROMPT = """You are JARVIS. Follow these rules:
1. Provide brief, direct answers without introductions
2. Only introduce yourself if specifically asked
3. Focus on key facts and current information
4. Use natural, professional tone without unnecessary formalities
5. Keep responses under 2-3 sentences unless more detail is required"""

CHAT_LOG_PATH = os.path.join("Data", "ChatLog.json")
os.makedirs("Data", exist_ok=True)

# Initialize chat history
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []

# Optimized constants
CACHE_TIMEOUT = 300  # 5 minutes cache
SEARCH_TIMEOUT = 10  # Increased to 10 seconds search timeout
MAX_SEARCH_RESULTS = 1
RESPONSE_MAX_TOKENS = 60  # Shorter responses for speed

# Add caching
search_cache = {}

def google_search(query, timeout=SEARCH_TIMEOUT):
    """Fast Google search with caching"""
    # Check cache first
    cache_key = query.lower().strip()
    current_time = time.time()
    
    if cache_key in search_cache:
        if current_time - search_cache[cache_key]['timestamp'] < CACHE_TIMEOUT:
            return search_cache[cache_key]['result']
    
    try:
        results = list(search(query, 
                            num_results=MAX_SEARCH_RESULTS, 
                            advanced=True, 
                            timeout=timeout))
        if results:
            result = results[0]
            search_result = f"{result.title} ({result.url})" if hasattr(result, 'title') else None
            
            # Cache the result
            search_cache[cache_key] = {
                'result': search_result,
                'timestamp': current_time
            }
            return search_result
    except Exception as e:
        print(f"Search error: {e}")
    return None

def fetch_search_results(query):
    """Fetch and parse search results with increased timeout"""
    try:
        results = []
        for result in search(query, num_results=MAX_SEARCH_RESULTS, timeout=SEARCH_TIMEOUT):
            try:
                response = requests.get(result, timeout=8)  # Increased timeout
                soup = BeautifulSoup(response.text, 'html.parser')
                # Get title and first paragraph
                title = soup.title.string if soup.title else ""
                desc = soup.find('p').text if soup.find('p') else ""
                results.append(f"{title}: {desc[:200]}...")
            except Exception as page_error:
                print(f"Page fetch error: {page_error}")
                continue
            if len(results) >= 2:  # Get at least 2 good results
                break
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

def get_groq_response(messages):
    """Optimized Groq API call with Cohere fallback"""
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=RESPONSE_MAX_TOKENS,
            top_p=1,
            stream=False  # Disable streaming for speed
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API error: {e}")
        # Fallback to Cohere
        try:
            # Convert messages to Cohere format
            if len(messages) >= 2:
                user_message = messages[-1]["content"]
                system_message = messages[0]["content"] if messages[0]["role"] == "system" else SYSTEM_PROMPT
                
                response = cohere_client.chat(
                    model="command-r-plus",
                    message=user_message,
                    preamble=system_message,
                    temperature=0.7,
                    max_tokens=RESPONSE_MAX_TOKENS
                )
                return response.text.strip()
        except Exception as cohere_error:
            print(f"Cohere fallback also failed: {cohere_error}")
        return "I couldn't process that request."

def get_groq_response(query, search_results=None):
    """Get AI response with context and Cohere fallback"""
    try:
        # Prepare context
        context = ""
        if search_results:
            context = f"Context from search: {' | '.join(search_results)}\n"
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{context}Answer briefly: {query}"}
        ]

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=100,  # Reduced for brevity
            top_p=1,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API error: {e}")
        # Fallback to Cohere
        try:
            full_query = f"{context}Answer briefly: {query}" if context else query
            response = cohere_client.chat(
                model="command-r-plus",
                message=full_query,
                preamble=SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=100
            )
            return response.text.strip()
        except Exception as cohere_error:
            print(f"Cohere fallback also failed: {cohere_error}")
        return None

def process_user_input(prompt):
    """Efficient processing with parallel execution"""
    global messages
    
    # Keep history small for faster context processing
    messages = messages[-5:]
    messages.append({"role": "user", "content": prompt})
    
    system_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Quick keyword check for search necessity
    needs_search = any(w in prompt.lower() for w in ['latest', 'news', 'current', 'today', 'recent'])
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        search_future = executor.submit(google_search, prompt) if needs_search else None
        groq_future = executor.submit(get_groq_response, system_messages + messages[-2:])
        
        try:
            # Increased timeout for search
            search_result = search_future.result(timeout=5) if search_future else None
            if search_result:
                context = f"Based on this: {search_result}, "
                messages[-1]["content"] = context + messages[-1]["content"]
        except concurrent.futures.TimeoutError:
            pass
        
        try:
            # Increased timeout for response
            response = groq_future.result(timeout=8)
        except concurrent.futures.TimeoutError:
            response = "I'll keep this brief due to time constraints."
    
    # Clean response
    response = response.split('\n')[0].strip()
    messages.append({"role": "assistant", "content": response})
    
    # Async save in background
    threading.Thread(target=lambda: save_messages_to_file(messages), daemon=True).start()
    
    return response

def RealtimeSearchEngine(query):
    """Main function to handle search and response"""
    try:
        # First try direct AI response
        direct_response = get_groq_response(query)
        if direct_response and len(direct_response) > 50:
            return direct_response

        # If response is too short or failed, try with search
        search_results = fetch_search_results(query)
        if search_results:
            response = get_groq_response(query, search_results)
            if response:
                return response

        # Fallback response if no good results
        return "I'm having trouble finding specific information about that. Could you please rephrase your question?"

    except Exception as e:
        print(f"Error in RealtimeSearchEngine: {e}")
        return "I encountered an error while processing your request. Please try again."

def save_messages_to_file(msgs):
    """Async message saving"""
    try:
        with open(CHAT_LOG_PATH, "w") as f:
            json.dump(msgs, f)
    except Exception as e:
        print(f"Error saving messages: {e}")

def main():
    print(f"{ASSISTANTNAME}: Ready.")
    
    while True:
        try:
            prompt = input("You: ").strip()
            if not prompt:
                continue
                
            if prompt.lower() in ('exit', 'quit', 'bye'):
                print(f"{ASSISTANTNAME}: Goodbye!")
                break
                
            response = process_user_input(prompt)
            print(f"{ASSISTANTNAME}: {response}")
            
        except KeyboardInterrupt:
            print(f"\n{ASSISTANTNAME}: Goodbye!")
            break
        except Exception:
            print(f"{ASSISTANTNAME}: Error occurred.")

if __name__ == "__main__":
    main()
