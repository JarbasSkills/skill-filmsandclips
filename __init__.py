from os.path import join, dirname

from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_utils.parse import fuzzy_match
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
from youtube_archivist import YoutubeMonitor


class FilmsAndClipsSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super().__init__("FilmsAndClips")
        self.supported_media = [MediaType.MOVIE,
                                MediaType.GENERIC]
        self.skill_icon = self.default_bg = join(dirname(__file__), "ui", "filmsandclips_icon.jpg")
        self.archive = YoutubeMonitor(db_name="FilmsAndClips",
                                      min_duration=30 * 60,
                                      logger=LOG,
                                      blacklisted_kwords=["trailer", "teaser", "movie scene",
                                                          "movie clip", "behind the scenes",
                                                          "Movie Preview", "Clip #",
                                                          "soundtrack", " OST", "opening theme"])

    def initialize(self):
        # per lang channel
        if self.lang.startswith("en"):
            url = "https://www.youtube.com/channel/UCbRPdPJpFz4f4pHeIhEck2w"
        elif self.lang.startswith("es"):
            url = "https://www.youtube.com/channel/UCO2thUSgz78cRlAVW5iP3pw"
        elif self.lang.startswith("it"):
            url = "https://www.youtube.com/channel/UCGoazA0Z4aoBccf3cdrBRfA"
        elif self.lang.startswith("de"):
            url = "https://www.youtube.com/channel/UCZl0iSBsqAiY59Ni_0vRVfw"
        elif self.lang.startswith("fr"):
            url = "https://www.youtube.com/channel/UCwOmaHmbjx5J_jG5IAg2Eqw"
        elif self.lang.startswith("pt"):
            url = "https://www.youtube.com/channel/UCcG2X4bDgt1qbaKKlcQTXpg"
        else:  # main channel
            url = "https://www.youtube.com/c/FilmandClips"
        bootstrap = f"https://raw.githubusercontent.com/OpenJarbas/streamindex/main/{self.archive.db.name}.json"
        self.archive.bootstrap_from_url(bootstrap)
        self.archive.monitor(url)
        self.archive.setDaemon(True)
        self.archive.start()

    # matching
    def match_skill(self, phrase, media_type):
        score = 0
        if self.voc_match(phrase, "movie") or media_type == MediaType.MOVIE:
            score += 40
        return score

    def normalize_title(self, title):
        title = title.lower().strip()
        title = self.remove_voc(title, "movie")
        title = title.replace("|", "").replace('"', "") \
            .replace(':', "").replace('”', "").replace('“', "") \
            .strip()
        return " ".join(
            [w for w in title.split(" ") if w])  # remove extra spaces

    def calc_score(self, phrase, match, base_score=0):
        score = base_score
        score += 100 * fuzzy_match(phrase.lower(), match["title"].lower())
        return min(100, score)

    def get_playlist(self, score=50, num_entries=250):
        pl = [{
            "title": video["title"],
            "image": video["thumbnail"],
            "match_confidence": 70,
            "media_type": MediaType.MOVIE,
            "uri": "youtube//" + video["url"],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "bg_image": video["thumbnail"],
            "skill_id": self.skill_id
        } for video in self.archive.sorted_entries()][:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "bg_image": self.default_bg,
            "title": "FilmsAndClips (Movie Playlist)",
            "author": "FilmsAndClips"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = self.match_skill(phrase, media_type)
        if self.voc_match(phrase, "filmsandclips"):
            yield self.get_playlist(base_score)
        if media_type == MediaType.MOVIE:
            # only search db if user explicitly requested movies
            phrase = self.normalize_title(phrase)
            for url, video in self.archive.db.items():
                yield {
                    "title": video["title"],
                    "author": "Full Free Films",
                    "match_confidence": self.calc_score(phrase, video, base_score),
                    "media_type": MediaType.MOVIE,
                    "uri": "youtube//" + url,
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": self.default_bg
                }

    @ocp_featured_media()
    def featured_media(self):
        return self.get_playlist()['playlist']


def create_skill():
    return FilmsAndClipsSkill()
