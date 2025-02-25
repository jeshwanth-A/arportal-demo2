# Use official Node.js image
FROM node:18

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first (for better caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the project files
COPY . .

# Build the React app
RUN npm run build

# Install serve to host the app
RUN npm install -g serve

# Expose the correct port
EXPOSE 8080

# Start the app
CMD ["serve", "-s", "build", "-l", "8080"]