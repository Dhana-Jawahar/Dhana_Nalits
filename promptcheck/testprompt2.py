from openai import OpenAI
import os

# Initialize the client. 
client = OpenAI(
    api_key=os.environ.get("API_KEY"),
    base_url="https://llm.nalits.com/v1"
)

# Step 1: Start the conversation
first_response = client.responses.create(
    model="gpt-oss:120b",
    input="Recommend three interesting story books for 10 year olds.",
    instructions="You are a helpful bookstore assistant."
)
print("First Output:", first_response.output_text)

# Step 2: Follow up by referencing the first response's ID
second_response = client.responses.create(
    model="gpt-oss:120b",
    input="Which one is the shortest?",
    previous_response_id=first_response.id  # Chains the context automatically
)
print("Follow-up Output:", second_response.output_text)

