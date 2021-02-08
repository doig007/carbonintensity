FROM python:3.6-slim-buster
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD exec gunicorn --bind :$carbonintensity_port --workers 1 --threads 8 --timeout 0 app.app:app
