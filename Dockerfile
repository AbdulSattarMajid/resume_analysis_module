# 1. Start with a lightweight version of Python
FROM python:3.11-slim

# 2. Install the Java Runtime (The missing piece)
# 'default-jre' is what LanguageTool needs to run its server
RUN apt-get update && apt-get install -y default-jre && apt-get clean;

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy and install your Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all your project files (main.py, engine folder, data folder)
COPY . .

# 6. Start the FastAPI server
# We use port 8080 inside the container
CMD ["uvicorn main:app --host 0.0.0.0 --port 8080"]