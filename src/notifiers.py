import httpx

from alerts import ServiceAlert


class ConsoleNotifier:
    def notify(self, alert: ServiceAlert):
        message = (
            f"\N{Bus} Service alert for {alert.authority}: "
            f'{", ".join(alert.affected_services)}\n{alert.description}'
        )
        if alert.link:
            message += f"\n{alert.link}"
        print(message)


class PushbulletNotifier:
    PUSHBULLET_PUSH_URL = "https://api.pushbullet.com/v2/pushes"

    def __init__(self, key: str, device_id: str | None):
        self.key = key
        self.device_id = device_id

    def notify(self, alert: ServiceAlert):
        data = {
            "type": "note",
            "title": (
                f"\N{Bus} Service alert for {alert.authority}: "
                f'{", ".join(alert.affected_services)}'
            ),
            "body": alert.description,
        }

        if alert.link:
            data["url"] = alert.link
            data["type"] = "link"
            data["body"] += "\n\nTap for more information."
        if self.device_id:
            data["device_iden"] = self.device_id

        headers = {"Access-Token": self.key}

        httpx.post(self.PUSHBULLET_PUSH_URL, json=data, headers=headers)
