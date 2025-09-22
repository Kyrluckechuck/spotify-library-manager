# Optimized frontend Dockerfile with better caching
ARG VITE_API_URL

# =============================================================================
# Stage 1: Base Node setup (cached unless Node version changes)
# =============================================================================
FROM node:20-alpine AS node-base
WORKDIR /app
RUN apk add --no-cache yarn

# =============================================================================
# Stage 2: Dependencies (cached unless package files change)
# =============================================================================
FROM node-base AS deps
COPY package.json yarn.lock ./
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN yarn install --frozen-lockfile

# =============================================================================
# Stage 3: Source code (rebuilds when source changes)
# =============================================================================
FROM deps AS source
COPY . .

# =============================================================================
# Stage 4: Test (for CI/CD)
# =============================================================================
FROM source AS test
RUN yarn test:run

# =============================================================================
# Stage 5: Build (for production)
# =============================================================================
FROM source AS build
RUN yarn build

# =============================================================================
# Stage 6: Production (nginx serving)
# =============================================================================
FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Default target
FROM production
