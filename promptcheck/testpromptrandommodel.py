from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("API_KEY"),
    base_url="https://llm.nalits.com/v1"
)
try:
    print("Sending request to Gemini...")

    response = client.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": "You are a Excellent poet."
            },
            {
                "role": "user",
                "content": "Tell me a short beautiful poem for a 8 year old for her birthday in rhyming way in English."
            }
        ]
    )

    print("\nPoem:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\nSomething went wrong.")
    print(f"Error: {e}")