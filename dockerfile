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

# Expose port for App Platform
ENV PORT=8080
EXPOSE 8080

# Run streamlit app (expand $PORT properly)
CMD ["sh", "-c", "streamlit run login.py --server.port=$PORT --server.address=0.0.0.0"]

