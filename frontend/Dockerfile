FROM node:18-alpine

WORKDIR /app

# Copy package descriptors and install dependencies
COPY package*.json ./
RUN npm ci

# Copy frontend application code
COPY . .

# Build argument for Next.js env var
ARG NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js application
RUN npm run build

EXPOSE 3000

# Start Next.js production server
CMD ["npm", "start"]
