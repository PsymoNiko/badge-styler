FROM nginx:alpine

# Install node and npm for potential future backend development
RUN apk add --no-cache nodejs npm

# Copy the static files to nginx html directory
COPY . /usr/share/nginx/html/

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for JSON files and ensure proper permissions
RUN mkdir -p /usr/share/nginx/html/badge_categories && \
    chmod -R 755 /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
