#!/bin/sh
# Start Uvicorn in the background (listening on localhost:8000)
uvicorn main:app --host 127.0.0.1 --port 8000 &

# Start Nginx in the foreground to keep the container running
nginx -g "daemon off;"