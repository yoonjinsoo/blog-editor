from ..services.crawlers.keyword_crawler import KeywordCrawler

class PostGenerator:
    def __init__(self, client_id, client_secret, crawler=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.crawler = crawler or KeywordCrawler(client_id=client_id, client_secret=client_secret)
        # ...existing code...
