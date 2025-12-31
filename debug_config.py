"""Debug script to check configuration and API connectivity."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

print("=" * 60)
print("DEBUG: Configuration Check")
print("=" * 60)

api_key = os.getenv("OPENROUTER_API_KEY")
api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
model = os.getenv("MODEL", "glm-4")

print(f"API Base URL: {api_base}")
print(f"Model: {model}")
print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'None'}...")
print(f"API Key length: {len(api_key) if api_key else 0}")

if not api_key:
    print("\n[ERROR] OPENROUTER_API_KEY is not set!")
    exit(1)

print("\n" + "=" * 60)
print("DEBUG: Testing API Connection")
print("=" * 60)

try:
    llm = ChatOpenAI(
        base_url=api_base,
        api_key=api_key,
        model=model,
        temperature=0.7,
    )
    print(f"ChatOpenAI client created successfully")
    print(f"Client model: {llm.model_name}")
    
    # Try a simple invocation
    from langchain_core.messages import HumanMessage, SystemMessage
    
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Say 'Hello, world!'")
    ]
    
    print("\nAttempting simple API call...")
    response = llm.invoke(messages)
    print(f"Response: {response.content}")
    print("\n[SUCCESS] API call succeeded!")
    
except Exception as e:
    print(f"\n[ERROR] API call failed: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
