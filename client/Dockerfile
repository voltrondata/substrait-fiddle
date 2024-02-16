FROM node:18-alpine as builder

ARG VITE_SESSION_SECRET
ENV VITE_SESSION_SECRET=$VITE_SESSION_SECRET

WORKDIR /app
COPY . .

RUN npm ci
RUN npm run build

FROM nginx:stable-alpine
WORKDIR /app/static
COPY --from=builder /app/dist .
COPY nginx.conf /etc/nginx/nginx.conf
