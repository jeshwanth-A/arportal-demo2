# Use a lightweight web server
FROM nginx:alpine

# Remove the default config and add a custom one
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy HTML files to Nginx
COPY . /usr/share/nginx/html

# Expose the correct port
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
