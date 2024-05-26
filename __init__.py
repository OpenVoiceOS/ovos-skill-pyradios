from os.path import join, dirname
from typing import Generator

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators import ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from pyradios import RadioBrowser
from rapidfuzz.distance import DamerauLevenshtein


class PyradiosSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(supported_media = [MediaType.RADIO],
                         skill_icon=join(dirname(__file__), "res", "radio-tuner.png"),
                         *args, **kwargs)
        self.radio_browser = RadioBrowser()

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
            for ch in self.radio_browser.search(name=query):
                score = base_score + int(DamerauLevenshtein.normalized_similarity(ch["name"], query) * 80)
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
