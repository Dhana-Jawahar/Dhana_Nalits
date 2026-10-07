from openai import OpenAI
import os
from pydantic import BaseModel, Field

client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),  # Fetch from Google AI Studio
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


# 1. Define your blueprint using Pydantic
class CharacterList(BaseModel):
    characternames:list[str] = Field(description="List of Main characters.")
    characterspeciality:list[str] = Field(description="List of Main characters speciality.")      
    
# 2. Make the API call incorporating both features
response = client.beta.chat.completions.parse(
    model="gemini-3.8-flash",
    messages=[
        {"role": "system", "content": "You are a professional Reader. Always output valid JSON matching the schema."},
        {"role": "user", "content": "Give me a quick main character list from Harry Potter and the Philosopher's Stone and their speciality in two words."}
    ],
    # --- Inference Parameters ---
    temperature=0.1,       # Low temperature ensures strict compliance & factual accuracy
    # max_tokens=1000,        # Limit the response length
    
    # --- Structured JSON Output ---
    response_format=CharacterList # Forces the model to adhere to the schema
)
# response.choices[0].message.content will contain the raw text output, while response.choices[0].message.parsed will contain the structured data.
print(response.choices[0].message.content)
# Safely parse the structured response
CharacterList_data = response.choices[0].message.parsed
print(f"Main Characters: {CharacterList_data.characternames}")
print(f"Specialities: {CharacterList_data.characterspeciality}")