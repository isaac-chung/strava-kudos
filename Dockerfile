FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

ENV STRAVA_EMAIL=
ENV STRAVA_PASSWORD=

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "give_kudos.py"]