FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run", "--debug"]