import os
from typing import Generator

from ovos_utils.ocp import MediaType, PlaybackType
# from ovos_utils.log import LOG
from ovos_workshop.decorators import ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from pyradios import RadioBrowser
from dead_simple_cache import SimpleCache
from rapidfuzz.distance import DamerauLevenshtein


BASE_DIR = os.getenv("HOME") or os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE_PATH = os.path.join(BASE_DIR, ".cache", "pyradios")


class PyradiosSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(
            supported_media = [MediaType.RADIO],
            skill_icon=os.path.join(
                os.path.dirname(__file__),
                "res",
                "radio-tuner-small.png"
            ),
            *args,
            **kwargs
        )
        self.cache = SimpleCache(file_path=DEFAULT_CACHE_PATH, open=False)
        self.radio_browser = RadioBrowser()

    def __del__(self):
        # Makes cache persistent on disk
        self.cache.close()

    def search_cache(self, query: str) -> list:
        """Search for cached stations."""
        items = self.cache.get(query, fuzzy=True)
        server_alive = {}
        for key, stations in items.items():
            for station in stations:
                url = station["url"]
                # Check whether each server is alive
                if url not in server_alive:
                    # TODO: find a faster way to check whether each server is up
                    # response = requests.head(url, timeout=1)
                    # code = response.status_code
                    # server_alive[url] = str(code).startswith('2') or str(code).startswith('3')
                    server_alive[url] = True
                if not server_alive[url]:
                    stations.remove(station)
        for key, stations in items.items():
            if stations:
                self.cache.replace(key=key, data=stations)
            else:
                self.cache.delete(key=key)
        return sum(list(items.values()), [])

    def search(self, query: str) -> list:
        """General search method."""
        # NOTE: make the cache persistent
        self.cache.open()
        # Search for cached items
        cached_items = self.search_cache(query)
        if cached_items:
            stations = cached_items
        else:
            # Search again
            stations = self.radio_browser.search(name=query, hidebroken=True)
            # Update cache
            for station in filter(lambda s: s["name"] != '', stations):
                self.cache.add(key=query, data=station)
        # NOTE: make the cache persistent
        self.cache.close()
        return stations

    @ocp_search()
    def search_pyradios(self, phrase: str, media_type: MediaType) -> Generator[dict, None, None]:
        """Search radio with Pyradios."""
        base_score = 0

        if media_type == MediaType.RADIO or self.voc_match(phrase, "radio"):
            base_score += 30
        else:
            base_score -= 30

        if self.voc_match(phrase, "pyradios"):
            base_score += 50  # explicit request
            phrase = self.remove_voc(phrase, "pyradios")

        queries = []
        if "radio" in phrase:
            phrase_without_radio = ' '.join(phrase.replace('radio', '').split())
            queries.append(phrase_without_radio)
        queries.append(phrase)
        for query in queries:
            for ch in self.search(query=query):
                score = base_score + int(DamerauLevenshtein.normalized_similarity(ch["name"], query) * 80)
                # LOG.debug(f"Query: {query}, match: {ch['name']}, score: {score}")
                yield {
                    "match_confidence": min(100, score),
                    "media_type": MediaType.RADIO,
                    "uri": ch["url_resolved"],
                    "playback": PlaybackType.AUDIO,
                    "image": ch["favicon"],
                    "bg_image": "",  # TODO: which image to add here?
                    "skill_icon": self.skill_icon,
                    "title": ch["name"],
                    "artist": ch["name"],
                    "author": "Pyradios",
                    "length": 0
                }
