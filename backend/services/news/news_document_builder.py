from models.news import NewsArticle
from models.company import Company

class NewsDocumentBuilder:
    """
    Builds natural language documents for news articles to be indexed into the Knowledge Base.
    """
    
    @staticmethod
    def build_news_doc(article: NewsArticle, company: Company) -> str:
        """
        Creates a rich, natural language document from a NewsArticle model.
        """
        pub_date = article.published_at.strftime("%B %d, %Y") if article.published_at else "Unknown Date"
        
        doc = (
            f"News Article regarding {company.name}.\n"
            f"Headline: {article.headline}\n"
            f"Source: {article.source}\n"
            f"Published: {pub_date}\n\n"
            f"Summary:\n{article.summary}\n\n"
            f"This article provides recent news updates and context regarding {company.name}'s activities, "
            f"partnerships, product launches, or market presence as of {pub_date}."
        )
        return doc
