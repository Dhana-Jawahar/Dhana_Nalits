from fastapi import FastAPI
# Create the FastAPI app instance
app = FastAPI()
# Define a simplee GET endpoint
@app.get("/")
def read_root():
   return {"message": "Hello, World!"}
# Define an endpoint with a path parameter
@app.get("/greet/{name}")
def greet_user(name: str):
   return {"message": f"Hello, {name}!"}


# from fastapi import FastAPI
# import psycopg

# app = FastAPI()

# # PostgreSQL connection
# conn = psycopg.connect(
#     host="localhost",
#     port=5432,
#     dbname="dbbook",
#     user="test_user",
#     password="Password123"
# )


# @app.get("/")
# def home():
#     return {"message": "Database connected!"}