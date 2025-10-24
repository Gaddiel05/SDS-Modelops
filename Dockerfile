# Choose a base image
FROM python:3.11-slim

# Install system-level dependencies
# Needed for building some Python packages (like pandas, numpy) if not using wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
    
# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Set the working directory in the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the application files
COPY main.py .
COPY models/model.pkl ./models/
COPY Templates/ ./Templates/

# Change ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose the FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Set the startup command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
