from scraper_api import ScraperAPIClient
from scholarly import scholarly, ProxyGenerator


class ScraperAPI(ProxyGenerator):
    def __init__(self, api_key):
        self._api_key = api_key
        self._client = ScraperAPIClient(api_key)

        assert api_key is not None

        super(ScraperAPI, self).__init__()

        self._TIMEOUT = 120
        self._session = self._client
        self._session.proxies = {}

    def _new_session(self):
        self.got_403 = False
        return self._session

    def _close_session(self):
        pass  # no need to close the ScraperAPI client
