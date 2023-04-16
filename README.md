# Bus alerts

Scrape bus service alerts from key authorities. Send them anywhere.

Right now this is set up for West Yorkshire, England buses only. The provided
sources are [WY Metro](https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/)
and [First Bus West Yorkshire Twitter](https://twitter.com/FirstWestYorks).
However, this is extensible, and you can add your own.

The built-in notifiers are console (prints to stdout) and [Pushbullet](https://www.pushbullet.com/).

The app runs entirely on GitHub via Actions.

## Installation and usage

1. Fork this repo.
2. Open `src/main.py` and edit the list of service numbers that you're
interested in.
3. For Pushbullet, change the device ID and provide your API key as a
[GH secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets).
4. Open `.github/workflows/notify.yml` and adjust the cron schedule for when
you want to check for alerts.

Advanced usage and setup of new alert services and notifiers is not documented.
