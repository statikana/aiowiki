from dataclasses import dataclass
from typing import Optional



@dataclass
class SearchPageResult:
    id: int
    key: str
    title: str
    excerpt: str
    matched_title: Optional[str]
    description: Optional[str]
    thumbnail: Optional["MediaData"]

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            thumbnail=MediaData.from_json(data.pop("thumbnail")),
            **data
        )


@dataclass
class MediaData:
    mimetype: str
    size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]
    url: str

    @classmethod
    def from_json(cls, data: dict):
        return cls(**data)