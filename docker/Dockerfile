FROM python:3.12

WORKDIR /app

COPY app /app
COPY app/requirements.txt /app/requirements.txt
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt update && apt install -y netcat-traditional

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
