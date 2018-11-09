FROM mohaseeb/raspberrypi3-python-opencv:latest

# This is to bypass platform detection in packages such as picamera
ENV READTHEDOCS True

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /tmp
RUN git clone https://github.com/RPi-Distro/RTIMULib/ RTIMU
WORKDIR /tmp/RTIMU/Linux/python
RUN python ./setup.py build
RUN python ./setup.py install

RUN pip install sense-hat

COPY . /usr/src/app
WORKDIR /usr/src/app

CMD ["python","-u","main.py"]
