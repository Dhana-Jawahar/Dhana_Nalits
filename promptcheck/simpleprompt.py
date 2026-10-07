from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),  # Fetch from Google AI Studio
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-3.8-flash",
    messages=[
         {
                    "role": "user",
                    "content": "Write a one-sentence bedtime story about a unicorn.",
          }
    ],
    temperature=0.9,
    max_tokens=60
    # ,extra_body={
    #   'extra_body': {
    #     "google": {
    #       "thinking_config": {
    #         "thinking_level": "low",
    #         "include_thoughts": True
    #       }
    #     }
    #   }
    # }
)
print(response.choices[0].message.content)
