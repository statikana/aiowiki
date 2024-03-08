from dataclasses import dataclass
import datetime
from typing import Optional



@dataclass
class SearchPageResult:
    id: int
    "Page identifier"

    key: str
    "Page title in URL-friendly format"

    title: str
    "Page title in reading-friendly format"

    excerpt: str
    """
    For search content endpoint:
        A few lines giving a sample of page content with search terms highlighted with <span class=\"searchmatch\"> tags. Excerpts may end mid-sentence.
    For search titles endpoint:
        Page title in reading-friendly format."""
    
    matched_title: Optional[str] = None
    "Title of the page redirected from, if the search term matched a redirect page, or None if search term did not match a redirect page"
    description: Optional[str] = None
    "Short summary of the page or None if no description exists"
    thumbnail: Optional["Thumbnail"] = None
    "Reduced-size version of the page's lead image or None if no lead image exists"

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            thumbnail=Thumbnail.from_json(thumb) if (thumb := data.pop("thumbnail")) else None,
            **data
        )


@dataclass
class Thumbnail:
    mimetype: str
    "The MIME type of the image, e.g. image/jpeg or video/mp4"
    url: str
    "The URL of the image or video"
    size: Optional[int] = None
    "The size of the image or video in bytes, or None if unknown"
    width: Optional[int] = None
    "The width of the image or video in pixels, or None if unknown"
    height: Optional[int] = None
    "The height of the image or video in pixels, or None if unknown"
    duration: Optional[int] = None
    "The duration of the video in seconds, or None if the media is an image"

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            url=f"https:{data.pop('url')}",
            **data
        )


@dataclass
class MostRead:
    date: datetime.date
    "The date of the most read articles"
    articles: list[ViewedArticle]
    "A list of the 50 most read articles for this date"
    

@dataclass
class FeaturedContent:
    tfa: TFA
    "Today's featured article"
    mostread: MostRead
    "Most read article yesterday"
    image: FullImage
    "Picture of the day (via Commons)"
    news: MostRead