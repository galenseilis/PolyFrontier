FROM python:3.9

WORKDIR /worker

COPY ./requirements.txt /worker/requirements.txt

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install --no-cache-dir --compile --upgrade -r /worker/requirements.txt

COPY ./app /worker/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
