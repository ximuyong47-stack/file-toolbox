FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libreoffice-common libreoffice-writer libreoffice-calc default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

ENV PORT=5000
ENV LIBREOFFICE_PATH=libreoffice

EXPOSE 5000
CMD ["python", "app.py"]
