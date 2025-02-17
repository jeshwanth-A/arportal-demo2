# Use an Nginx base image
FROM nginx:alpine

# Copy index.html to the default Nginx directory
COPY index.html /usr/share/nginx/html/index.html

# Expose port 8080 (Cloud Run expects this)
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
