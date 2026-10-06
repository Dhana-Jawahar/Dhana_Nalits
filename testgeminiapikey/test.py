# from google import genai

# client = genai.Client()

# interaction = client.interactions.create(
#     model="gemini-3.8-flash",
#     # input="Explain how AI works in a few words"
#     input="Two Amazing Fact  about AI"
# )
# print(interaction.output_text)

# import base64
# from google import genai

# client = genai.Client()

# interaction = client.interactions.create(
#     model="gemini-3.1-flash-image",
#     input="Generate an image of a beautiful city skyline at sunset",
# )

# with open("generated_image.png", "wb") as f:
#     f.write(base64.b64decode(interaction.output_image.data))

# from openai import OpenAI
# import os

# client = OpenAI(
#     api_key=os.environ.get("GEMINI_API_KEY"),
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )

# response = client.chat.completions.create(
#     model="gemini-3.8-flash",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a helpful assistant."
#         },
#         {
#             "role": "user",
#             "content": "Explain to me how AI works"
#         }
#     ]
# )
# print(response.choices[0].message)

import base64
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="Generate an image of a beautiful city skyline at sunset",
)

with open("generated_image.png", "wb") as f:
    f.write(base64.b64decode(interaction.output_image.data))
