from openai import OpenAI
import os


name=input("Enter your name: ")
client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),  # Fetch from Google AI Studio
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=30.0
)

try:
    print("Sending request to Gemini...")
    response = client.chat.completions.create(
    model="gemini-3.8-flash",
     reasoning_effort="low",
    messages=[
         {
                    "role": "user",
                    "content": f"say Hello and Greet in a one short sentence {name}.",
                    
          }
    ],
    temperature=0.1,       # Low temperature ensures strict compliance & factual accuracy
    max_tokens=500
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
    print("\nGemini response:")
    print(response.choices[0].message.content)
except Exception as e:
    print("\nSomething went wrong.")

    error_text = str(e).lower()

    if "quota" in error_text or "rate limit" in error_text or "429" in error_text:
        print("Gemini API quota/limit has been reached.")
        print("Please wait for the quota to reset or check your Gemini API usage.")

    elif "timeout" in error_text:
        print("The request timed out.")
        print("Gemini did not respond within 30 seconds.")

    elif "401" in error_text or "authentication" in error_text:
        print("Authentication failed.")
        print("Please check your GEMINI_API_KEY.")

    else:
        print(f"Error: {e}")