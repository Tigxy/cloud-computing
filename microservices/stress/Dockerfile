FROM python:3.8-slim-buster

LABEL auther=rendstrasser@gmail.com

WORKDIR /opt

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]