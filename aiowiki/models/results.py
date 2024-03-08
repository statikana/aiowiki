from dataclasses import dataclass, fields
import datetime
from enum import Enum
from typing import Any, Optional, get_args
from aiowiki.constants import PRIMITIVES

from aiowiki.models.enums import ArticleType, ArticleURLs, Language, LanguageDirection


@dataclass
class JSONSerializeable:
    @classmethod
    def from_json(cls, data: dict):
        constructed = dict()

        for member in fields(cls):
            value: Any
            typ = member.type
            if isinstance(member.type, Optional):
                if data[member.name] is None:
                    value = None
                else:
                    typ = get_args(member.type)[0]  # internal of Optional (Optional[int] -> int)
            if isinstance(typ, PRIMITIVES):
                value = data[member.name]
            else:
                if isinstance(typ, JSONSerializeable):
                    value = typ.from_json(data[member.name])
                elif isinstance(typ, Enum):
                    value = typ(data[member.name])
                else:
                    raise ValueError("unimplemented deserialization source")
            
            constructed[member.name] = value
        
        return cls(**constructed)


class SearchPageResult(JSONSerializeable):
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


class Thumbnail(JSONSerializeable):
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


class MostReadArticle(JSONSerializeable):
    "Represents an article within the mostread section of featured content"

    views: int
    "Nunmber of views"
    rank: int
    "View rank. This may not start with 1 and may not be sequential."
    view_history: list["ViewShapshot"]
    type: ArticleType
    "Type of artcle"
    namespace: "ArticleNamespace"
    "Article namespace"
    wikibase_item: str
    "Wikidata identifier"
    titles: "ArticleTitles"
    "Article title in multiple formats"
    pageid: int
    "Article identifier"
    thumbnail: "BasicImage"
    "Reduced-size version of the article's lead image"
    originalimage: "BasicImage"
    "Original-size version of the article's lead image"
    lang: Language
    "Language of the article"
    dir: LanguageDirection
    "Language direction"
    revision: str
    "Revision identifier for the latest revision"
    tid: str
    "Time-based UUID used for rendering content changes"
    timestamp: datetime
    "Time when the article was last edited"
    description: str
    "Short summary of the article"
    description_source: str
    """Source of the description: local for descriptions maintained within the 
    page or central for descriptions imported from Wikidata"""
    content_urls: ArticleURLs
    "Article URLs"
    extract: str
    "First several sentences of the article in plain text"
    extract_html: str
    "First several sentences of the article in simplified HTML"

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            view_history=[ViewShapshot.from_json(snap) for snap in data.pop("view_history")],
            type=ArticleType(data.pop("type")),
            namespace=ArticleNamespace.from_json(data.pop("namespace")),
            titles=ArticleTitles.from_json(data.pop("titles")),
            thumbnail=BasicImage.from_json(data.pop("thumbnail")),
            originalimage=BasicImage.from_json(data.pop("thumbnail")),
            lang=Language(data.pop("lang")),
            dir=LanguageDirection(data.pop("dir")),
            content_urls=ArticleURLs.from_json(data.pop("content_urls")),
            **data
        )


class ArticleNamespace(JSONSerializeable):
    id: int
    "Namespace identifier"
    text: str
    "Localized name of the namespace"


class ViewShapshot(JSONSerializeable):
    date: datetime.date
    views: int

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            date=datetime.date.fromisoformat(data.pop("date")),
            **data
        )


class ArticleTitles(JSONSerializeable):
    canonical: str
    "Article title in URL-friendly format"
    normalized: str
    "Article title with underscores replaced with spaces"
    display: str
    "Article title in reading-friendly format"



class MostRead(JSONSerializeable):
    date: datetime.date
    "The date of the most read articles"
    articles: list[MostReadArticle]
    "A list of the 50 most read articles for this date"

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            date=datetime.date.fromisoformat(data.pop("date")),
            articles=[MostReadArticle.from_json(article) for article in data.pop("articles")]
        )


class BasicImage(JSONSerializeable):
    source: str
    "Image URL"
    width: int
    "Image width in pixels"
    height: int
    "Image height in pixels"


class News(JSONSerializeable):
    story: str
    links: list[]
    

class FeaturedContent(JSONSerializeable):
    tfa: TFA
    "Today's featured article"
    mostread: MostRead
    "Most read article yesterday"
    image: FullImage
    "Picture of the day (via Commons)"
    news: News


class TFA(JSONSerializeable):
