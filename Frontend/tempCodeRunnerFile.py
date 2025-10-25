import cohere
from rich import print
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("cohereAPIKey")

if not CohereAPIKey:
    print("[bold red]Error:[/bold red] Cohere API key not found in environment variables.")
    exit(1)

# Initialize cohere client
co = cohere.Client(CohereAPIKey)

# Define available functions
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

messages = []
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', etc.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.'
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

ChatHistory = [
    {"role": "user", "content": "How are you?"},
    {"role": "assistant", "content": "general how are you"},
    {"role": "user", "content": "do you like pizza?"},
    {"role": "assistant", "content": "general do you like pizza"},
    {"role": "user", "content": "open chrome and tell me about mahatma gandhi."},
    {"role": "assistant", "content": "open chrome, general tell me about mahatma gandhi."},
    {"role": "user", "content": "open chrome and firefox?"},
    {"role": "assistant", "content": "open chrome, open firefox"},
    {"role": "user", "content": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "assistant", "content": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "user", "content": "chat with me."},
    {"role": "assistant", "content": "general chat with me."}
]

def FirstLayerDMM(prompt: str = "test", recursion_depth: int = 0, max_recursion_depth: int = 5):
    if recursion_depth > max_recursion_depth:
        print("[bold red]Error:[/bold red] Maximum recursion depth reached.")
        return ["general (query)"]

    messages.append({"role": "user", "content": f"{prompt}"})

    try:
        stream = co.chat_stream(
            model='command-r-plus',
            message=prompt,
            temperature=0.7,
            chat_history=ChatHistory,
            prompt_truncation='OFF',
            connectors=[],
            preamble=preamble
        )

        response = ""
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text

        response = response.replace("\n", "")
        response = response.split(",")

        response = [i.strip() for i in response]
        temp = []
        for task in response:
            for func in funcs:
                if task.startswith(func):
                    temp.append(task)

        response = temp

        if "(query)" in response:
            newresponse = FirstLayerDMM(prompt=prompt, recursion_depth=recursion_depth + 1, max_recursion_depth=max_recursion_depth)
            return newresponse
        else:
            return response
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        return ["general (query)"]

if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>> ")))