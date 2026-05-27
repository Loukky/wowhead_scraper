"""实时写入 Items 到 JSON 文件，线程安全"""
import json
import os
import threading
from pathlib import Path


class IncrementalJsonPipeline:
    """每个 item 抓取后立即追加写入 JSON 文件（线程安全）"""

    def __init__(self):
        self.file = None
        self.first_item = True
        self.lock = threading.Lock()

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        feed_uri = crawler.settings.get("INCREMENTAL_OUTPUT_PATH")
        if feed_uri:
            path = Path(feed_uri)
            path.parent.mkdir(parents=True, exist_ok=True)
            # 清空或创建文件，写入开头 [
            pipeline.file = path.open("w", encoding="utf-8")
            pipeline.file.write("[\n")
            pipeline.first_item = True
        return pipeline

    def process_item(self, item, spider):
        if self.file:
            with self.lock:
                line = json.dumps(item, ensure_ascii=False, indent=2)
                if self.first_item:
                    self.file.write(line)
                    self.first_item = False
                else:
                    self.file.write(",\n" + line)
                self.file.flush()
                os.fsync(self.file.fileno())  # 立即刷到磁盘
        return item

    def close_spider(self, spider):
        if self.file:
            with self.lock:
                self.file.write("\n]")
                self.file.close()
