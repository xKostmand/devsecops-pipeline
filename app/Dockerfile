# Intentional Vulnerability: Using an older base image and running as root
FROM python:3.8-slim

# Intentional Vulnerability: Exposing secrets inside the Dockerfile
ENV APP_SECRET_KEY="dockerfile_hardcoded_secret_key"
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies (bad practice: no --no-cache-dir, and installing curl which adds attack surface)
RUN apt-get update && apt-get install -y curl sqlite3 && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port (exposing more ports than needed is a security smell, but let's expose 5000)
EXPOSE 5000

# Running as root is the default, which is an intentional security smell for Trivy to detect.
CMD ["python", "app.py"]
