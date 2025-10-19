import contextlib
import os
import sqlite3
import tomllib
from typing import Annotated

import pydantic

from alerts import WYMetroAlertService, FirstBusAlertService, ServiceAlert
from notifiers import ConsoleNotifier, PushbulletNotifier


class BusAlertsConfig(pydantic.BaseModel):
    services: Annotated[set[str], pydantic.Field(min_length=1)]
    ignore_urls: set[str] = set()


def _load_config_file(fp: os.PathLike) -> BusAlertsConfig:
    try:
        with open(fp, "rb") as f:
            config_file = tomllib.load(f)
    except FileNotFoundError:
        return BusAlertsConfig()
    return BusAlertsConfig.model_validate(config_file)


def _setup_db(fp: os.PathLike) -> sqlite3.Connection:
    conn = sqlite3.connect(fp)
    conn.row_factory = sqlite3.Row

    with conn:
        conn.execute("""\
CREATE TABLE IF NOT EXISTS sent_alerts(
    authority TEXT NOT NULL,
    description TEXT NOT NULL,
    affected_services TEXT NOT NULL,
    link TEXT,
    sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)""")

    return conn


def _save_alert_to_db(conn: sqlite3.Connection, alert: ServiceAlert) -> None:
    alert_flat = {
        "authority": alert.authority,
        "description": alert.description,
        "affected_services": ",".join(alert.affected_services),
        "link": alert.link,
    }
    with conn:
        conn.execute("INSERT INTO sent_alerts(authority, description, affected_services, link) VALUES(:authority, :description, :affected_services, :link)", alert_flat)


def _load_alerts_from_db(conn: sqlite3.Connection) -> list[ServiceAlert]:
    with conn:
        cur = conn.execute("SELECT * FROM sent_alerts")
        rows = cur.fetchall()
    alerts = []
    for row in rows:
        affected_services = set(clean_service for service in row["affected_services"].split(",") if (clean_service := service.strip()))
        parsed_alert = ServiceAlert(
            authority=row["authority"],
            description=row["description"],
            affected_services=affected_services,
            link=row["link"],
        )
        alerts.append(parsed_alert)
    return alerts


def _create_wymetro_ignore_list(config: BusAlertsConfig, sent_alerts: list[ServiceAlert] | None = None) -> set[str]:
    if not sent_alerts:
        return config.ignore_urls

    already_sent = set()
    for alert in sent_alerts:
        # skip wrong authority
        if alert.authority.lower().strip() != "wy metro":
            continue
        # skip if services not matching requested
        if alert.affected_services != config.services:
            continue
        already_sent.add(alert.link)

    return config.ignore_urls | already_sent


def main() -> None:
    config = _load_config_file("config.toml")
    conn = _setup_db("storage.db")

    with contextlib.closing(conn):
        sent_alerts = _load_alerts_from_db(conn)
        ignore_list = _create_wymetro_ignore_list(config=config, sent_alerts=sent_alerts)

        alert_services = [
            WYMetroAlertService(service_list=config.services, ignore_list=ignore_list),
        ]

        notifiers = [
            PushbulletNotifier(
                key=os.environ["PUSHBULLET_API_KEY"], device_id="ujD4MLyzAqGsjyDuV8VNkq"
            ),
            # ConsoleNotifier(),
        ]

        for service in alert_services:
            alerts = list(service.find_alerts())
            for notifier in notifiers:
                for alert in alerts:
                    notifier.notify(alert)
                    _save_alert_to_db(conn=conn, alert=alert)


if __name__ == "__main__":
    main()
