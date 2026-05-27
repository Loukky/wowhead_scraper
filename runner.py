import os

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from scrapy.crawler import CrawlerProcess

from spiders import ItemSpider, NPCSpider, ObjectSpider, QuestSpider, QuestXpSpider
from utils.paths import OUTPUT_DIR


class Runner:
    lang: str = ""
    target: str = ""
    version: str = ""
    concurrent: int = 3
    delay: float = 2.0
    target_dir: Path = None

    def __init__(self, lang: str, target: str, version: str, concurrent: int = 3, delay: float = 2.0) -> None:
        self.lang = lang
        self.target = target
        self.version = version
        self.concurrent = concurrent
        self.delay = delay
        self.logger = getLogger(__name__)
        self.target_dir = OUTPUT_DIR / target
        if not self.target_dir.exists():
            self.target_dir.mkdir()
        self.target_dir = self.target_dir.relative_to(os.path.dirname(os.path.realpath(__file__)))

    def run(self) -> None:
        feed_uri = self.target_dir / (self.lang + "_data.json")
        if feed_uri is None:
            return None
        if feed_uri.exists():
            self.logger.info("Removing existing '{}' file".format(feed_uri))
            feed_uri.unlink()

        process = CrawlerProcess(settings={
            "LOG_LEVEL": "INFO",
            "CONCURRENT_REQUESTS": self.concurrent,
            "CONCURRENT_REQUESTS_PER_DOMAIN": self.concurrent,
            "DOWNLOAD_DELAY": self.delay,
            "RANDOMIZE_DOWNLOAD_DELAY": True,
            "AUTOTHROTTLE_ENABLED": False,
            "RETRY_ENABLED": True,
            "RETRY_HTTP_CODES": [429, 500, 502, 503, 504],
            "RETRY_TIMES": 2,
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "DEFAULT_REQUEST_HEADERS": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
            },
            "COOKIES_ENABLED": True,
            "FEED_URI": str(feed_uri),
            "FEED_FORMAT": "json",
            "FEED_EXPORT_INDENT": None,
        })

        # Proxy support: set WOWHEAD_PROXY env var to route through a proxy
        proxy_url = os.environ.get("WOWHEAD_PROXY")
        if proxy_url:
            self.logger.info("Using proxy: %s", proxy_url)
            process.settings.setdict({
                "HTTPPROXY_ENABLED": True,
                "PROXY": proxy_url,
            }, priority="cmdline")

        self.logger.info("Starting {} crawler".format(self.target))
        self.logger.info("Output goes to '{}'".format(feed_uri))
        if self.target == "item":
            process.crawl(ItemSpider, lang=self.lang, version=self.version)
        elif self.target == "npc":
            process.crawl(NPCSpider, lang=self.lang, version=self.version)
        elif self.target == "object":
            process.crawl(ObjectSpider, lang=self.lang, version=self.version)
        elif self.target == "quest":
            process.crawl(QuestSpider, lang=self.lang, version=self.version)
        elif self.target == "xp":
            process.crawl(QuestXpSpider, lang=self.lang, version=self.version)

        process.start()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-l", "--lang", help="The language you want to scrape. Default: 'en'", type=str)
    parser.add_argument("-t", "--target", help="The target you want to scrape."
                                               "Possible values are 'npc', 'quest', 'item', 'object' and 'xp'. Default: 'npc'", type=str)
    parser.add_argument("-v", "--version", help="The version of WoW Classic you want to scrape."
                                                "Possible values are 'classic', 'tbc', 'wotlk', 'mop'. Default: 'wotlk'", type=str)
    parser.add_argument("-c", "--concurrent", help="Number of concurrent requests. Default: 3", type=int, default=3)
    parser.add_argument("-d", "--delay", help="Download delay in seconds. Default: 2.0", type=float, default=2.0)
    args = parser.parse_args()

    if args.lang is None:
        args.lang = "en"
    if args.target is None:
        args.target = "npc"
    if args.version is None:
        args.version = 'wotlk'

    runner = Runner(args.lang, args.target, args.version, args.concurrent, args.delay)
    runner.run()
