# SamadhanX Frontend Dockerfile
# Multi-stage build for optimized Next.js application

# ===================================
# Stage 1: Base Node.js Environment
# ===================================
FROM node:18-alpine AS base

# Install dependencies only when needed
RUN apk add --no-cache libc6-compat

# Set working directory
WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# ===================================
# Stage 2: Dependencies Installation
# ===================================
FROM base AS dependencies

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# ===================================
# Stage 3: Build Stage
# ===================================
FROM base AS builder

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies (including devDependencies)
RUN npm ci

# Copy source code
COPY . .

# Set build environment variables
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

# Build the application
RUN npm run build

# ===================================
# Stage 4: Development Image
# ===================================
FROM base AS development

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies
RUN npm ci

# Copy source code
COPY . .

# Set development environment variables
ENV NODE_ENV development
ENV NEXT_TELEMETRY_DISABLED 1

# Change ownership to nextjs user
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Development command
CMD ["npm", "run", "dev"]

# ===================================
# Stage 5: Production Image
# ===================================
FROM base AS production

# Set production environment variables
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Copy built application from builder stage
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Copy production dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Change ownership to nextjs user
RUN chown -R nextjs:nodejs /app
USER nextjs

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Expose port
EXPOSE 3000

# Production command
CMD ["node", "server.js"]

# ===================================
# Stage 6: Nginx Static Serving (Alternative)
# ===================================
FROM nginx:alpine AS static

# Copy built static files
COPY --from=builder /app/out /usr/share/nginx/html

# Copy custom nginx configuration
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]