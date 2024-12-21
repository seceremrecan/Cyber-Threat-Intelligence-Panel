# Base image
FROM node:18

# Working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy frontend source code
COPY ./ ./

# Build frontend
RUN npm run build

# Expose port
EXPOSE 3000

# Start the frontend
CMD ["npm", "start"]
