# Strava Kudos Giver 👍👍👍

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) 

A Python tool to automatically give [Strava](https://www.strava.com) Kudos to recent activities on your feed. There are a few repos that uses JavaScript like [strava-kudos-lambda](https://github.com/mjad-org/strava-kudos-lambda) and [strava-kudos](https://github.com/rnvo/strava-kudos). 

The repo is set up so that the script runs on a set schedule via Github Actions. Github suggests in their [docs](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule) to not run cron jobs at the start of every hour to avoid delays so minute30 was chosen here. Feel free to change it to whenever you want.

## 🏃 Usage
1. Fork the repo
2. Setup the environment variables in secrets
3. Give kudos automatically!

Alternatively, you can run the script manually with
```
python3 give_kudos.py
```

## 🛠️Setup

### Playwright
[Playwright](https://github.com/microsoft/playwright-python) is used, so be sure to follow instructions to install it properly. 

### Environment Variables

Set the environment variables for your email and password as follows:
```
export STRAVA_EMAIL=YOUR_EMAIL
export STRAVA_PASSWORD=YOUR_PASSWORD
```

## 🔬Testing
Manual testing was done in Python 3.7.6. 

## Contributions
Let me know if you wish to add anything or if there are any issues!

[![ForTheBadge built-with-love](http://ForTheBadge.com/images/badges/built-with-love.svg)](https://GitHub.com/Naereen/)