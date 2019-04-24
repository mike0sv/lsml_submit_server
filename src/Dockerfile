FROM python:3.6

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt


WORKDIR /src
COPY * ./

CMD bash -c "python server.py"