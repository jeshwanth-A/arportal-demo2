# Use a lightweight web server
FROM nginx:alpine

# Copy HTML files to Nginx
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
