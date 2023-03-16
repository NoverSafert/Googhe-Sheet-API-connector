#Dockerfile
FROM python:3.10-slim
ENV PYTHONUNBUFFERED True
COPY requirements.txt /
RUN pip install -r /requirements.txt
RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
COPY app.py .
COPY connections.py .
COPY credentials.json .
COPY api-sheetdb-0253ee7a0d6f.json .
COPY token.json .
CMD ["gunicorn"  , "-b", "0.0.0.0:8888", "app:app"]
