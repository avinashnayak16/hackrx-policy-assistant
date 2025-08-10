import os
from dotenv import load_dotenv
load_dotenv()
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def gemini_chat(prompt: str) -> str:
    url = f"{GEMINI_API_BASE_URL}/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    json_data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=json_data)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError):
        return f"Unexpected response: {data}"

if not GEMINI_API_KEY:
    print("No GEMINI_API_KEY found in environment.")
else:
    try:
        result = gemini_chat("What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?")
        print("Gemini API key is working. Response:", result)
    except Exception as e:
        print("Gemini API key test failed:", e)