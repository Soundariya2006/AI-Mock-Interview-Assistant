import os
from dotenv import load_dotenv
from google import genai

# Load variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env")
    exit()

# Create Gemini client
client = genai.Client(api_key=api_key)

# Send a simple test question
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Say hello to my AI Mock Interview Assistant project."
)

print("✅ Gemini is working!")
print()
print("Gemini response:")
print(response.text)