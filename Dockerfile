FROM python:3.8.5-alpine

RUN mkdir -p /inet-trouble-app

WORKDIR /inet-trouble-app

ENV FLASK_ENV=development
ENV FLASK_APP=wsgi.py

COPY . /inet-trouble-app

RUN pip install -r requirements.txt

EXPOSE 5050

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5050"]
