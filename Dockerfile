FROM mohaseeb/raspberrypi3-python-opencv:latest

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app

CMD ["python","-u","main.py"]
