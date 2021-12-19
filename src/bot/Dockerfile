FROM python:3.9

WORKDIR /opt
RUN mkdir -p app
WORKDIR ./app

# Install requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY main.py ./

# Run the app
ENTRYPOINT python main.py