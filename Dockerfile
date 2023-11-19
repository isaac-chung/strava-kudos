FROM ubuntu:22.04

RUN apt update && apt-get -y install python3-pip
WORKDIR /app
ADD requirements.txt .
RUN pip3 install -r requirements.txt
RUN playwright install
ADD *.py /app/

ENV STRAVA_EMAIL ""
ENV STRAVA_PASSWORD ""

ENTRYPOINT [ "python3", "./give_kudos.py" ]
