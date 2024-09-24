flask db init
flask db migrate -m "First migration."
flask db upgrade
python3 run_server.py