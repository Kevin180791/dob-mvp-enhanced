FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create static directory for Swagger UI
RUN mkdir -p static
RUN curl -L https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css -o static/swagger-ui.css
RUN curl -L https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js -o static/swagger-ui-bundle.js

# Expose port
EXPOSE 3001

# Set environment variables
ENV PORT=3001
ENV HOST=0.0.0.0

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]

