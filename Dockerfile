FROM python:3.7
ADD ./app /app
ADD requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run_parser.py"]