import os

from alerts import WYMetroAlertService, FirstBusAlertService
from notifiers import ConsoleNotifier, PushbulletNotifier


def main():
    services = {"16", "16A"}
    wymetro_ignore = {
        "https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/kirkgate-leeds-city-centre-1/",
        "https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/kirkgate-harper-street-leeds-city-centre-1/",
        "https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/armleygyratory-3/",
        "https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/abbeydash-2/",
        "https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/lightnight/",
    }

    alert_services = [
        WYMetroAlertService(service_list=services, ignore_list=wymetro_ignore),
        # FirstBusAlertService(service_list=services),
    ]

    notifiers = [
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
