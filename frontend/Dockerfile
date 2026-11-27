# Multi-stage build: node:22-alpine compiles the React/Vite app in the build stage.
# Only the compiled static assets are copied into the nginx:1.27-alpine runtime stage,
# so Node, npm and all dev dependencies are discarded — the final image is ~10 MB
# instead of ~400 MB and has no Node process or build toolchain in production.
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
