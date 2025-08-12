ARG VITE_API_URL=http://localhost:5000/graphql

FROM node:20-alpine AS build
WORKDIR /app
RUN apk add --no-cache yarn
COPY package.json yarn.lock ./
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
