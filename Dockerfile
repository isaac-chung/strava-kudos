FROM python:3.9

WORKDIR /app
ADD requirements.txt .
RUN pip3 install -r requirements.txt
RUN playwright install
ADD *.py /app/

ENV STRAVA_EMAIL ""
ENV STRAVA_PASSWORD ""

ENTRYPOINT [ "python3", "./give_kudos.py" ]
