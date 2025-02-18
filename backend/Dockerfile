# Use a slim Python image with specific version for stability
FROM python:3.10-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Create and switch to non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*

# Copy application code
COPY . .

# Create an entrypoint script
RUN echo '#!/bin/sh\nuvicorn main:app --host 0.0.0.0 --port ${PORT}' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE ${PORT}

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]