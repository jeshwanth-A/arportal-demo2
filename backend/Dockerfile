FROM python:3.9-slim

# Install Nginx and necessary packages
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Remove default Nginx config and add our custom config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code (.py files, .env, etc.)
COPY . .

# Create directory for storing 3D models
RUN mkdir -p /app/models

# Copy the startup script and grant execution rights
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port 8080 for Nginx (public)
EXPOSE 8080

# Run the startup script that launches Uvicorn and Nginx
CMD ["/start.sh"]