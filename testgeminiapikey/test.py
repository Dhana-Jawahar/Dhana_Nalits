# from openai import OpenAI
# import os
# import base64


# client = OpenAI(
#     api_key=os.environ.get("API_KEY"),
#     base_url="https://llm.nalits.com/v1/chat/completions/"
# )
# try:
#     print("Sending request to Gemini...")

#     interaction = client.interactions.create(
#         model="gemini-3.1-flash-image",
#         input="Create a simple image of a red apple on a white background.",
#     )

#     if interaction.output_image:
#         with open("apple.png", "wb") as f:
#             f.write(base64.b64decode(interaction.output_image.data))

#         print("Image generated successfully: apple.png")
#     else:
#         print("No image was returned.")

# except Exception as e:
#     print("\nSomething went wrong.")

#     error_text = str(e).lower()

#     if "quota" in error_text or "rate limit" in error_text or "429" in error_text:
#         print("Gemini API quota/limit has been reached.")
#         print("Please wait for the quota to reset or check your Gemini API usage.")

#     elif "timeout" in error_text:
#         print("The request timed out.")
#         print("Gemini did not respond within 30 seconds.")

#     elif "401" in error_text or "authentication" in error_text:
#         print("Authentication failed.")
#         print("Please check your GEMINI_API_KEY.")

#     else:
#         print(f"Error: {e}")

# import base64
# from google import genai

# client = genai.Client()

# try:
#     print("Sending request to Gemini...")
#     interaction = client.interactions.create(
#     model="gemini-3.1-flash-image",
#     input="Generate an image of a Rickmansworth Lake in the style of a watercolor painting, with soft pastel colors and gentle brush strokes. " \
#     "The scene should include a serene lake surrounded by lush greenery, with a few ducks swimming in the water. " \
#     "The sky should be a light blue with fluffy white clouds, and the overall mood should be peaceful and calming.",
#     timeout=30.0 
#     )

#     with open("generated_image.png", "wb") as f:
#         f.write(base64.b64decode(interaction.output_image.data))
    
# except Exception as e:
#     print("\nSomething went wrong.")

#     error_text = str(e).lower()

#     if "quota" in error_text or "rate limit" in error_text or "429" in error_text:
#         print("Gemini API quota/limit has been reached.")
#         print("Please wait for the quota to reset or check your Gemini API usage.")

#     elif "timeout" in error_text:
#         print("The request timed out.")
#         print("Gemini did not respond within 30 seconds.")

#     elif "401" in error_text or "authentication" in error_text:
#         print("Authentication failed.")
#         print("Please check your GEMINI_API_KEY.")

#     else:
#         print(f"Error: {e}")

from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("API_KEY"),
    base_url="https://llm.nalits.com/v1/chat/completions/"
)

response = client.chat.completions.create(
    model="gemini-3.8-flash",
    messages=[
        {
            "role": "system",
            "content": "You are a Excellent poet."
        },
        {
            "role": "user",
            "content": "Tell me a beautiful poem for a 8 year oldfor her bithday."
        }
    ]
)
print(response.choices[0].message)


# from google import genai
# import base64

# client = genai.Client()

# interaction = client.interactions.create(
#     model="gemini-nano-banana-2.1",
#     input="A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat. It's munching on a green bamboo leaf. The design features bold, clean outlines, simple cel-shading, and a vibrant color palette. The background must be white.",
# )

# for step in interaction.steps:
#     if step.type == "model_output":
#         for content_block in step.content:
#             if content_block.type == "text":
#                 print(content_block.text)
#             elif content_block.type == "image":
#                 with open("red_panda_sticker.png", "wb") as f:
#                     f.write(base64.b64decode(content_block.data))

# from openai import OpenAI
# import os


# name=input("Enter your name: ")
# client = OpenAI(
#     api_key=os.environ.get("GEMINI_API_KEY"),  # Fetch from Google AI Studio
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#     timeout=30.0
# )

# try:
#     print("Sending request to Gemini...")
#     response = client.chat.completions.create(
#     model="gemini-3.8-flash",
#      reasoning_effort="low",
#     messages=[
#          {
#                     "role": "user",
#                     "content": f"say Hello and Greet in a one short sentence {name}.",
                    
#           }
#     ],
#     temperature=0.1,       # Low temperature ensures strict compliance & factual accuracy
#     max_tokens=500
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
#     )
#     print("\nGemini response:")
#     print(response.choices[0].message.content)
# except Exception as e:
#     print("\nSomething went wrong.")

#     error_text = str(e).lower()

#     if "quota" in error_text or "rate limit" in error_text or "429" in error_text:
#         print("Gemini API quota/limit has been reached.")
#         print("Please wait for the quota to reset or check your Gemini API usage.")

#     elif "timeout" in error_text:
#         print("The request timed out.")
#         print("Gemini did not respond within 30 seconds.")

#     elif "401" in error_text or "authentication" in error_text:
#         print("Authentication failed.")
#         print("Please check your GEMINI_API_KEY.")

#     else:
#         print(f"Error: {e}")