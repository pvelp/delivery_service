bind = "0.0.0.0:8000"
module = "config.wsgi"

workers = 4  # Adjust based on your server's resources
worker_connections = 1000
threads = 4

# certfile = "/etc/nginx/certs/server.crt"
# keyfile = "/etc/nginx/certs/server.key"
