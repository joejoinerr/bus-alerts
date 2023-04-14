import os

from alerts import WYMetroAlertService, FirstBusAlertService
from notifiers import ConsoleNotifier, PushbulletNotifier


SERVICES = {"4"}


def main():
    wymetro_ignore = {
        "https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/newstationstbishopgatest/",
        "https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/city-square/",
    }

    alert_services = [
        WYMetroAlertService(service_list=SERVICES, ignore_list=wymetro_ignore),
        FirstBusAlertService(service_list=SERVICES),
    ]

    notifiers = [
        ConsoleNotifier(),
        PushbulletNotifier(
            key=os.environ["PUSHBULLET_API_KEY"], device_id="ujD4MLyzAqGsjyDuV8VNkq"
        ),
    ]

    for service in alert_services:
        alerts = list(service.find_alerts())
        for notifier in notifiers:
            for alert in alerts:
                notifier.notify(alert)


if __name__ == "__main__":
    main()
