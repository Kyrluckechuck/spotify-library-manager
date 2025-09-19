ARG VITE_API_URL

FROM node:20-alpine AS build
WORKDIR /app
RUN apk add --no-cache yarn
COPY package.json yarn.lock ./
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN yarn install --frozen-lockfile
COPY . .

# Test stage - can be used for running tests
FROM build AS test
RUN yarn test:run

# Build stage - continues from build
FROM build AS build-dist
RUN yarn build

# Production stage
FROM nginx:alpine
COPY --from=build-dist /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
