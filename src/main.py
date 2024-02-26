import os

from alerts import WYMetroAlertService, FirstBusAlertService
from notifiers import ConsoleNotifier, PushbulletNotifier


def main():
    services = {"16"}
    wymetro_ignore = set()

    alert_services = [
        WYMetroAlertService(service_list=services, ignore_list=wymetro_ignore),
        FirstBusAlertService(service_list=services),
    ]

    notifiers = [
        # ConsoleNotifier(),
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
