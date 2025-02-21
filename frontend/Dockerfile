# Use official Node.js image
FROM node:18

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package.json package-lock.json ./

# Install dependencies (caches layers to speed up builds)
RUN npm install

# Copy rest of the project files
COPY . .

# Build the React app
RUN npm run build

# Install a lightweight web server for Cloud Run
RUN npm install -g serve

# Expose the correct port for Cloud Run
EXPOSE 8080

# Serve the built React app on port 8080
CMD ["serve", "-s", "build", "-l", "8080"]