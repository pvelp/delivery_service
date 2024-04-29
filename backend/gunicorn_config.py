bind = "0.0.0.0:8000"
module = "config.wsgi"

workers = 4  # Adjust based on your server's resources
worker_connections = 1000
threads = 4

# certfile = "/etc/letsencrypt/live/shashlikns.ru/fullchain.pem"
# keyfile = "/etc/letsencrypt/live/shashlikns.ru/fullchain.pem"
