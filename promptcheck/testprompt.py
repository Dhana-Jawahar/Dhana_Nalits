from openai import OpenAI
import os

# Initialize the OpenAI client pointing to Google's gateway
client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),  # Fetch from Google AI Studio
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-3.8-flash",
    messages=[
        {   "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain to me how AI works"
        }
    ]
)

print(response.choices[0].message.content)
