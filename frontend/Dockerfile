# Production Dockerfile for Mobile App
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Set build-time environment variable for API URL
ARG VITE_API_BASE_URL=http://localhost:6501
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 6503

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:6503 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
