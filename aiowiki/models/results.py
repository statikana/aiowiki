import datetime
from typing import Optional

from aiowiki.models.enums import ArticleType, ArticleURLs, Language, LanguageDirection
from aiowiki.models.internal import InterfaceModel


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
    text: Optional[str]
    "Artist name in plain text, if available"
    name: str
    "Artist name"
    user_page: Optional[str]
    "User page for the artist on Wikimedia Commons, if available"


class Thumbnail(InterfaceModel):
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
    views: int


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

    matched_title: Optional[str] = None
    "Title of the page redirected from, if the search term matched a redirect page, or None if search term did not match a redirect page"
    description: Optional[str] = None
    "Short summary of the page or None if no description exists"
    thumbnail: Optional[Thumbnail] = None
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
    def from_json(cls, data: dict):
        captions = dict()

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


class Article(InterfaceModel):
    "Represents an article"
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
    thumbnail: BasicImage
    "Reduced-size version of the article's lead image"
    originalimage: BasicImage
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


class News(InterfaceModel):
    story: str
    "Short summary of the story in HTML"
    links: list[Article]
    "Articles related to the story"


class MostReadArticle(Article):
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
    tfa: Article
    "Today's featured article"
    mostread: MostRead
    "Most read article yesterday"
    image: FullImage
    "Picture of the day (via Commons)"
    news: News
