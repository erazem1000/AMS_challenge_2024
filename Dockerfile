# Using an official Python runtime as a parent image
FROM python:3.11-slim

# Setting environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/src/app/venv/bin:$PATH"

# Setting the working directory
WORKDIR /usr/src/app

# Installing system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copying the requirements file
COPY requirements.txt .

# Installing dependencies
RUN python -m venv venv && \
    venv/bin/pip install --upgrade pip && \
    venv/bin/pip install --no-cache-dir -r requirements.txt

# Copying the rest of the application
COPY . .

# Exposing a default port (optional)
EXPOSE 5000

# Adding health check to verify the server's status
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1


# Set executable permission and specify entrypoint
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

# # Setting a placeholder default command
# CMD ["bash", "-c", "echo 'Dobrodošel uporabnik!\\n Uredi podatke v compose.yaml datoteki in poženi docker-compose up.'"]