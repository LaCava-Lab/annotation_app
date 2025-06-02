# Use stable Python version
FROM python:3.10-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port for App Platform (DigitalOcean sets $PORT)
ENV PORT=8080
EXPOSE 8080

# Start Streamlit or your app (adjust as needed)
CMD ["streamlit", "run", "app.py", "--server.port=$PORT", "--server.enableCORS=false"]
