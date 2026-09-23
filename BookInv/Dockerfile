FROM python:3.14-slim          
WORKDIR /BookInv
COPY requirements.txt .      
RUN pip install -r requirements.txt 
COPY . .
#Run the Application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
