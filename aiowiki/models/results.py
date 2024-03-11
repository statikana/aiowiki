import datetime
from typing import Generic

from aiowiki.models.enums import ArticleType, Language, LanguageDirection, MediaType, PlatformType
from aiowiki.models.internal import InterfaceModel, PlatformT


class BasicImage(InterfaceModel):
    source: str
    "Image URL"
    width: int
    "Image width in pixels"
    height: int
    "Image height in pixels"


class Credit(InterfaceModel):
    html: str
    "Attribution description for the image in HTML"
    text: str
    "Attribution description for the image in plain text"


class Artist(InterfaceModel):
    html: str
    "Artist name in HTML"
    text: str | None
    "Artist name in plain text, if available"
    name: str | None
    "Artist name"
    user_page: str | None
    "User page for the artist on Wikimedia Commons, if available"


class EmbeddedImage(InterfaceModel):
    mimetype: str
    "The MIME type of the image, e.g. image/jpeg or video/mp4"
    url: str
    "The URL of the image or video"
    size: int | None = None
    "The size of the image or video in bytes, or None if unknown"
    width: int | None = None
    "The width of the image or video in pixels, or None if unknown"
    height: int | None = None
    "The height of the image or video in pixels, or None if unknown"
    duration: int | None = None
    "The duration of the video in seconds, or None if the media is an image"

    __prefix_schema__ = {
        "url": "https:"
    }


class Image(InterfaceModel):
    mediatype: MediaType
    "File type"
    size: int | None
    "File size in bytes"
    width: int | None
    "Image width in pixels"
    height: int | None
    "Image height in pixels"
    duration: int | None
    "Duration of the video, audio, or multimedia file "
    url: str
    "URL to download the image"


class User(InterfaceModel):
    id: int
    name: str


class RevisionMeta(InterfaceModel):
    timestamp: datetime.datetime
    user: User
    "Note: This is inconsistent with the API documentation. In the documentation, this is `id`"


class File(InterfaceModel):
    title: str
    "File title"
    file_description_url: str
    "URL for the page describing the file, including license information and other metadata"
    latest: RevisionMeta
    "Object containing information about the latest revision to the file"
    preferred: Image
    "Information about the file's preferred preview format"
    original: Image
    "Information about the file's original format"
    thumbnail: Image | None
    "get_file only: Information about the file's thumbnail format"

    __prefix_schema__ = {
        "file_description_url": "https:"
    }


class License(InterfaceModel):
    type: str
    "Name of the license in plain text"
    code: str
    "Code for the license. For example: cc-by-sa-4.0"
    url: str
    "URL for a page that describes the terms and conditions of the license"


class ImageDescription(InterfaceModel):
    html: str
    "Description of the image in HTML"
    text: str
    "Description of the image in plain text"
    lang: Language
    "The language the image's description is in"


class ArticleNamespace(InterfaceModel):
    id: int
    "Namespace identifier"
    text: str
    "Localized name of the namespace"


class ViewShapshot(InterfaceModel):
    date: datetime.date
    "Date of the view snapshot"
    views: int
    "Number of views for the article on the given date"


class SearchPageResult(InterfaceModel):
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

    matched_title: str | None = None
    "Title of the page redirected from, if the search term matched a redirect page, or None if search term did not match a redirect page"
    description: str | None = None
    "Short summary of the page or None if no description exists"
    thumbnail: EmbeddedImage | None = None
    "Reduced-size version of the page's lead image or None if no lead image exists"


class ArticleTitles(InterfaceModel):
    canonical: str
    "Article title in URL-friendly format"
    normalized: str
    "Article title with underscores replaced with spaces"
    display: str
    "Article title in reading-friendly format"


class ImageStructure(InterfaceModel):
    captions: dict[Language, str]
    "A dictionary of image captions in various languages"

    @classmethod
    def _from_json(cls: InterfaceModel, data: dict) -> InterfaceModel:
        captions = {}

        for lang, caption in data["captions"].items():
            captions[Language(lang)] = caption

        return cls(captions=captions)


class FullImage(InterfaceModel):
    title: str
    "Image page title"
    thumbnail: BasicImage
    "Preview-sized image"
    image: BasicImage
    "Full-sized image"
    file_page: str
    "URL for the image's attribution page"
    artist: Artist
    "Information about the image's author"
    credit: Credit
    "Attribution information. For more information about attribution, visit Credit line on Wikimedia Commons."
    license: License
    "License that the image is available under"
    description: str
    "Description of the image"
    wb_entity_id: str
    "Wikimedia Commons Wikibase (WB) identifier"
    structured: ImageStructure
    "Image captions and tags"


class PlatformArticle(InterfaceModel, Generic[PlatformT]):
    page: str
    "URL for the article"
    revisions: str
    "URL for the article's revision history"
    edit: str
    "URL for editing the article"
    talk: str
    "URL for the article's talk page"


class ArticleURLs(InterfaceModel):
    desktop: PlatformArticle[PlatformType.DESKTOP]
    "Article URLs for desktop viewing"
    mobile: PlatformArticle[PlatformType.MOBILE]
    "Article URLs for mobile viewing"


class ArticleMeta(InterfaceModel):
    "Represents metadata of an article"
    type: ArticleType
    "Type of artcle"
    namespace: ArticleNamespace
    "Article namespace"
    wikibase_item: str
    "Wikidata identifier"
    titles: ArticleTitles
    "Article title in multiple formats"
    pageid: int
    "Article identifier"
    thumbnail: BasicImage | None
    "Reduced-size version of the article's lead image, if available"
    originalimage: BasicImage | None
    "Original-size version of the article's lead image, if available"
    lang: Language
    "Language of the article"
    dir: LanguageDirection
    "Language direction"
    revision: str
    "Revision identifier for the latest revision"
    tid: str
    "Time-based UUID used for rendering content changes"
    timestamp: datetime.datetime
    "Time when the article was last edited"
    description: str | None
    "Short summary of the article, if available"
    description_source: str | None
    """Source of the description: local for descriptions maintained within the
    page or central for descriptions imported from Wikidata"""
    content_urls: ArticleURLs
    "Article URLs"
    extract: str
    "First several sentences of the article in plain text"
    extract_html: str
    "First several sentences of the article in simplified HTML"


class News(InterfaceModel):
    story: str
    "Short summary of the story in HTML"
    links: list[ArticleMeta]
    "Articles related to the story"


class MostReadArticle(ArticleMeta):
    "Represents an article within the mostread section of featured content"
    views: int
    "Nunmber of views"
    rank: int
    "View rank. This may not start with 1 and may not be sequential."
    view_history: list[ViewShapshot]
    "View history for the article"


class MostRead(InterfaceModel):
    "Represents the most read articles for a given date"
    date: datetime.date
    "The date of the most read articles"
    articles: list[MostReadArticle]
    "A list of the 50 most read articles for this date"


class FeaturedContent(InterfaceModel):
    "Represents the featured content for a given date"
    tfa: ArticleMeta
    "Today's featured article"
    mostread: MostRead
    "Most read article yesterday"
    image: FullImage
    "Picture of the day (via Commons)"
    news: list[News]


class UndatedEvent(InterfaceModel):
    "Describes someone's birth, death, or a notable event."

    text: str
    "The description of the event"
    pages: list[ArticleMeta]
    "Articles related to the event"


class DatedEvent(UndatedEvent):
    year: int
    "The year of the event"


class OnThisDay(InterfaceModel):
    selected: list[DatedEvent]
    "Curated set of events that occurred on the given date"
    births: list[DatedEvent]
    "Notable people born on the given date"
    deaths: list[DatedEvent]
    "Notable people who died on the given date"
    events: list[DatedEvent]
    "Events that occurred on the given date that are not included in another type"
    holidays: list[UndatedEvent]
    "Fixed holidays celebrated on the given date "
