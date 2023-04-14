import time
from collections.abc import Iterable
import dataclasses
import datetime
import re

import feedparser
import httpx
import requests_html


BUS_REGEX = re.compile(r"\b[a-zA-Z]*\d+[a-zA-Z]*\b")


def fetch_text_from_url(url: str) -> str:
    res = httpx.get(url, headers={"user-agent": requests_html.user_agent()})
    return res.text


@dataclasses.dataclass
class ServiceAlert:
    authority: str
    description: str
    affected_services: set
    link: str | None = None


class WYMetroAlertService:
    ALERT_URL = "https://www.wymetro.com/plan-a-journey/travel-news/bus-travel-alerts/"
    DOMAIN = "https://www.wymetro.com"
    AUTHORITY_NAME = "WY Metro"

    def __init__(
        self,
        service_list: list | set | None = None,
        ignore_list: list | set | None = None,
    ):
        self.service_list = set() if not service_list else set(service_list)
        self.ignore_list = set() if not ignore_list else set(ignore_list)

    @staticmethod
    def _services_text_to_set(services_text: str) -> set[str]:
        *_, services_text = services_text.split(":", maxsplit=1)
        services = BUS_REGEX.findall(services_text)
        return set(services)

    def _parse_alert(self, alert_html: requests_html.Element) -> ServiceAlert:
        alert_heading = alert_html.find("h3", first=True)
        alert_link = alert_heading.find("a", first=True).attrs["href"]
        alert_link = self.DOMAIN + alert_link.removeprefix(self.DOMAIN)
        services_text = alert_html.find("p", first=True).text
        alert_description = alert_heading.text + alert_html.find("p")[-1].text
        return ServiceAlert(
            authority=self.AUTHORITY_NAME,
            link=alert_link,
            description=alert_description,
            affected_services=self._services_text_to_set(services_text),
        )

    def find_alerts(self) -> Iterable[ServiceAlert]:
        html_str = fetch_text_from_url(self.ALERT_URL)
        doc = requests_html.HTML(html=html_str)
        news_list = doc.find("ul.newsitems li")
        for alert_html in news_list:
            alert = self._parse_alert(alert_html)
            relevant_services = (
                alert.affected_services
                if not self.service_list
                else alert.affected_services.intersection(self.service_list)
            )
            if not relevant_services or alert.link in self.ignore_list:
                continue
            alert.affected_services = relevant_services
            yield alert


class FirstBusAlertService:
    ALERT_URL = "https://nitter.net/FirstWestYorks/rss"
    AUTHORITY_NAME = "First Bus"

    def __init__(self, service_list: list | set | None = None):
        self.service_list = set() if not service_list else set(service_list)

    def _parse_alert(self, tweet_data: dict) -> ServiceAlert:
        tweet_title, tweet_description = tweet_data["title"].split("\n\n", maxsplit=1)
        affected_services = set(BUS_REGEX.findall(tweet_title))
        return ServiceAlert(
            authority=self.AUTHORITY_NAME,
            description=tweet_description,
            affected_services=affected_services,
        )

    def find_alerts(self) -> Iterable[ServiceAlert]:
        # xml = fetch_text_from_url(self.ALERT_URL)
        with open("rss.xml") as f:
            xml = f.read()
        rss = feedparser.parse(xml)
        today = datetime.date.today()
        today = datetime.datetime.combine(today, datetime.datetime.min.time())
        for tweet in rss.entries:
            if "service update" not in tweet.title.lower():
                continue
            pub_timestamp = time.mktime(tweet.published_parsed)
            pub_date = datetime.datetime.fromtimestamp(pub_timestamp)
            if pub_date < today:
                continue
            alert = self._parse_alert(tweet)
            relevant_services = (
                alert.affected_services
                if not self.service_list
                else alert.affected_services.intersection(self.service_list)
            )
            if not relevant_services:
                continue
            alert.affected_services = relevant_services
            yield alert
