FROM python:3.9.7

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app

CMD ["python", "app.py"]