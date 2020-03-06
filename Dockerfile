FROM python:3.7
COPY . .
RUN pip install flask
RUN pip install psycopg2
CMD ["python3", "run.py"]
