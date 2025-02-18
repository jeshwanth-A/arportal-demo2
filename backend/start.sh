#!/bin/sh
# Substitute the PORT env variable in the nginx config template
envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Start the FastAPI app with Uvicorn in the background (binding to localhost:8000)
uvicorn main:app --host 127.0.0.1 --port 8000 &

# Start Nginx in the foreground
nginx -g "daemon off;"