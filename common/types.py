from dataclasses import dataclass
from typing import List


@dataclass
class SearchQuery:
    car_brand: str
    car_model: str
    spare_part: str


@dataclass
class ScrapedItem:
    car_brand: str
    car_model: str
    spare_part: str
    url: str
    name: str
    images: List[str]
    description: str
    price_value: int
    price_currency: str
    seller_name: str
    seller_label: str
