FROM python:3.9-slim-buster

WORKDIR /opt
RUN mkdir -p app
WORKDIR /opt/app

# Install git as it is required in requirements.txt
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# Install requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app.py ./

# Run the app
ENTRYPOINT python app.py
