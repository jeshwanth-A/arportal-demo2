FROM python:3.9-slim

# Install Nginx and envsubst (from gettext-base)
RUN apt-get update && apt-get install -y nginx gettext-base && rm -rf /var/lib/apt/lists/*

# Remove default Nginx config and copy our template
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code and .env file
COPY . .

# Create directory for storing 3D models
RUN mkdir -p /app/models

# Copy the startup script and grant execution rights
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose the port that Cloud Run will use (default is provided by the PORT env variable)
EXPOSE ${PORT}

# Run the startup script that launches Uvicorn and Nginx
CMD ["/start.sh"]