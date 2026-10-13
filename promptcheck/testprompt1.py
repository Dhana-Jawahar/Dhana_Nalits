import os
from openai import OpenAI

# Initialize the client. 
client = OpenAI(
    api_key=os.environ.get("API_KEY"),
    base_url="https://llm.nalits.com/v1"
)

instructions="""You are a Math Teacher.
                1. You will be given a math problem.
                2. You will solve the problem step by step.
                3. You will provide the final answer at the end.
                4. You will provide the answer in a simple and easy to understand way.
               """
try:
    response = client.responses.create(
        model="gpt-oss:120b",
        instructions=instructions,
        input="There are 50 lockers in the gym.80% of them are used. How many lockers are empty?",
    )
    print(response.output_text)
except Exception as e:
    print(f"An error occurred: {e}")