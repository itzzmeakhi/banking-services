# ---- Stage 1: Build ----
FROM node:18-alpine

# Create app directory
WORKDIR /app

# Copy dependencies
COPY package*.json ./

# Install production dependencies
RUN npm install --production

# Copy source code
COPY . .

# Expose port (from .env or default)
EXPOSE 5001

# Start the service
CMD ["npm", "start"]
