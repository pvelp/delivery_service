# delivery_service

## Поднятие докерфайла:
- docker-compose build
- docker-compose up
- Далее открываете вторую консоль, так как предыдущая занята работой сервера
- docker ps
- Находите id для delivery_service:dev_back и копируете его
- docker exec -it <id> python backend/manage.py csu