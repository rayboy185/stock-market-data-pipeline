FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /root/.dbt && cp profiles.docker.yml /root/.dbt/profiles.yml

CMD ["dbt", "run"]
