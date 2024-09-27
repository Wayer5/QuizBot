if [ -z "$(ls -A migrations)" ]; then
  # Если директория migrations пустая, то:
  flask db init
  flask db migrate
else
  # Если имеет какие-то файлы:
  flask db migrate
fi
flask db upgrade
python3 run_server.py