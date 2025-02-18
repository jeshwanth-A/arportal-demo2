# Use a slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create an entrypoint script that uses the PORT environment variable
RUN echo '#!/bin/sh\nuvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Expose the expected port
EXPOSE 8080

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]