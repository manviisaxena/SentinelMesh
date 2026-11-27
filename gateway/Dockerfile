# nginx:1.27-alpine: minimal Alpine-based NGINX image (~10 MB). No application
# runtime is needed — only the reverse-proxy config is copied in. Baking the
# config into the image means the exact gateway routing is versioned and promoted
# as sentinelmesh-gateway rather than relying on a host bind mount in Kubernetes.
FROM nginx:1.27-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
