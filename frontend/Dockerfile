# Use Node.js as the base image
FROM node:16-alpine

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app
COPY . .

# Build the React app
RUN npm run build

# Install a lightweight static server to serve the build
RUN npm install -g serve

# Expose the port that serve will run on (can be adjusted)
EXPOSE 5000

# Serve the built app on port 5000
CMD ["serve", "-s", "build", "-l", "5000"]