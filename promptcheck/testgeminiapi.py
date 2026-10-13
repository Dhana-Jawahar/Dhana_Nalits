from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain how AI works in a two lines",    
    timeout=30.0
)
print(interaction.output_text)