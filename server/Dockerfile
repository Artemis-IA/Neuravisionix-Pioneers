FROM python:3.9-slim-buster
RUN apt-get update && apt-get install -y python3-opencv

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
VOLUME [ "/app" ]
CMD [ "python3", "app.py" ]