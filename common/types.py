from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional


@dataclass_json
@dataclass
class SearchQuery:
    car_brand: str
    car_model: str
    spare_part: str


@dataclass_json
@dataclass
class ScrapedItem:
    query: SearchQuery
    url: str
    title: str
    images: List[str]
    description: str
    price_value: Optional[int]
    price_currency: Optional[str]
    seller_name: str
    seller_label: str

    def csv_header():
        return ['car_brand', 'car_model', 'spare_part',
                'title', 'url', 'images', 'description', 'price_value',
                'price_currency', 'seller_name', 'seller_label']

    def as_csv_columns(self):
        result = [self.query.car_brand, self.query.car_model, self.query.spare_part]
        for col in ScrapedItem.csv_header()[3:]:
            result.append(getattr(self, col))
        return result
