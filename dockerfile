FROM python:3.10-slim

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the app
COPY . /app
WORKDIR /app

# Use $PORT from App Platform
CMD ["streamlit", "run", "app.py", "--server.port", "$PORT", "--server.enableCORS", "false"]
