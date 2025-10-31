#from dotenv import load_dotenv
from secret_key import OPENROUTER_API_KEY
import requests
from datetime import datetime
#import os

# Load all environment variables from the .env file
#load_dotenv()  

#api_key = os.getenv("OPENAI_API_KEY")
#print(api_key)

#OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter endpoint
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize OpenAI client
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define banned keywords for moderation
BANNED_KEYWORDS = ["kill", "hack", "bomb", "attack", "murder"]

# This function checks for banned keywords
def violates_policy(text):
    text_lower = text.lower()
    return any(word in text_lower for word in BANNED_KEYWORDS)

# This function redacts banned words
def redact_text(text):
    for word in BANNED_KEYWORDS:
        text = text.replace(word, "[REDACTED]")
    return text

# This function logs moderation events
def log_moderation(event_type, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("moderation_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {event_type.upper()} VIOLATION:\n{text}\n\n")

# The main AI chat function
def chat_with_ai(user_prompt):
    # Step 1: Input moderation
    if violates_policy(user_prompt):
        print("❌ Your input violated the moderation policy.")
        log_moderation("input", user_prompt)
        return

    # Step 2: Define system prompt (behavior guide)
    system_prompt = (
        "You are a helpful, friendly, and safe AI assistant. "
        "Never produce or promote harmful content."
    )

    # Step 3: Send to OpenAI API
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",  # or "gpt-3.5-turbo"
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt},
    #     ],
    # )

    # ai_reply = response.choices[0].message.content

    # Step 3: Make API request
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI Moderation Demo"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=data)

    if response.status_code != 200:
        print(f"❌ API Error {response.status_code}: {response.text}")
        return

    ai_reply = response.json()["choices"][0]["message"]["content"]

    # Step 4: Output moderation
    if violates_policy(ai_reply):
        log_moderation("output", ai_reply)
        ai_reply = redact_text(ai_reply)
        print("⚠️ Some content was redacted for safety.")
    
    print("\n AI Response:")
    print(ai_reply)

# Run it
if __name__ == "__main__":
    user_input = input("Enter your prompt: ")
    chat_with_ai(user_input)

 