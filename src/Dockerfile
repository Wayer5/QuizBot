
FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . src/

COPY settings.py .

COPY run_server.py .

CMD [ "bash", "src/command.sh" ]