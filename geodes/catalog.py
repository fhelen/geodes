# -*- coding: utf-8 -*-

from typing import List
from dataclasses import dataclass, asdict
import pandas as pd

from pygeodes import Geodes
from pygeodes import Config
import pygeodes



@dataclass
class Object:
    endpoint: str
    bucket: str
    prefix: str

@dataclass
class Meta:
    tile_name: str
    year: int
    month: int
    day: int
    sensor: str

@dataclass
class Row:
    Object: Object
    Meta: Meta
    cloud_cover: float

class UrlParser:
    def __init__(self, url: str) -> None:
        self.__url: str = url
        self.endpoint: str | None = None
        self.bucket: str | None = None
        self.prefix: str | None = None
        self.tile_name : str | None = None
        self.year: int | None = None
        self.month: int | None = None
        self.day: int | None = None
        self.sensor: str | None = None


    def parse(self):
        splits = self.__url.split("/")
        self.endpoint = splits[2]
        self.bucket = splits[3]
        self.prefix = "/".join(splits[4:])
        self.tile_name = splits[4]
        self.year = int(splits[5])
        self.month = int(splits[6])
        self.day = int(splits[7])
        self.sensor = splits[8].split("_")[0]


    def get_object(self) -> Object:
        return Object(endpoint=self.endpoint,
                      bucket=self.bucket,
                      prefix=self.prefix)

    def get_meta(self) -> Meta:
        return Meta(tile_name=self.tile_name,
                    year=self.year,
                    month=self.month,
                    day=self.day,
                    sensor=self.sensor)

class Catalog:
    def __init__(self,
                 conf: pygeodes.Config
                 ) -> None:
        self.__geodes = Geodes(conf=conf)

    def search_l2a(self,
                   tile_name: str,
                   start_date: str,
                   end_date: str) -> List[Row] | None:
        query = {
        "dataset": {"eq": "THEIA_REFLECTANCE_SENTINEL2_L2A"},
        "grid:code": {"eq": tile_name},
        "start_datetime": {"gte": start_date+"T00:00:00Z"},
        "end_datetime": {"lte": end_date+"T23:59:59Z"}
        }
        results, _ = self.__geodes.search_items(query=query,
                                                get_all=True)
        if len(results) == 0:
            return None
        rows = []
        for element in results:
            properties = element.to_dict()["properties"]
            parser = UrlParser(properties["endpoint_url"])
            parser.parse()
            rows.append(Row(Object=parser.get_object(),
                      Meta=parser.get_meta(),
                      cloud_cover=properties["eo:cloud_cover"]))
        return rows

if __name__ == '__main__':
    conf = Config(api_key="DaR6Shxv20x4oetSZzhP6Mj6VrdIPXvleCiXaZwjA6xod1YOAx",
                  logging_level="DEBUG")
    catalog = Catalog(conf)
    items = catalog.search_l2a(tile_name="T30TXQ",
                               start_date="2018-01-01",
                               end_date="2018-12-31")
    df = pd.json_normalize([asdict(element) for element in items])
    print(df[df["Meta.month"] > 5])
