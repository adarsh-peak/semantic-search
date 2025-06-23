FROM python:3.9-slim

WORKDIR /app

# Copy the .pem file into the container
COPY Netskopecert.pem /usr/local/share/ca-certificates/Netskopecert.pem

# Set all necessary environment variables
ENV CURL_CA_BUNDLE=/usr/local/share/ca-certificates/Netskopecert.pem \
    SSL_CERT_FILE=/usr/local/share/ca-certificates/Netskopecert.pem \
    GIT_SSL_CAPATH=/usr/local/share/ca-certificates/Netskopecert.pem \
    REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/Netskopecert.pem \
    NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/Netskopecert.pem

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]
