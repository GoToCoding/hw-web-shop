FROM python:3.7
COPY . .

RUN pip install flask
RUN pip install psycopg2
RUN pip install requests

CMD ["python3", "store_core/run.py"]
