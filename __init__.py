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

        bl = ["trailer", "teaser", "movie scene",
              "movie clip", "behind the scenes",
              "Movie Preview", "Clip #",
              "soundtrack", " OST", "opening theme"]
        self.archive = YoutubeMonitor(db_name="FilmsAndClips",
                                      min_duration=30 * 60,
                                      logger=LOG,
                                      blacklisted_kwords=bl)
        self.archive_en = YoutubeMonitor(db_name="FilmsAndClips_en",
                                         min_duration=30 * 60,
                                         logger=LOG,
                                         blacklisted_kwords=bl)
        self.archive_es = YoutubeMonitor(db_name="FilmsAndClips_es",
                                         min_duration=30 * 60,
                                         logger=LOG,
                                         blacklisted_kwords=bl)
        self.archive_it = YoutubeMonitor(db_name="FilmsAndClips_it",
                                         min_duration=30 * 60,
                                         logger=LOG,
                                         blacklisted_kwords=bl)
        self.archive_de = YoutubeMonitor(db_name="FilmsAndClips_de",
                                         min_duration=30 * 60,
                                         logger=LOG,
                                         blacklisted_kwords=bl)
        self.archive_fr = YoutubeMonitor(db_name="FilmsAndClips_fr",
                                         min_duration=30 * 60,
                                         logger=LOG,
                                         blacklisted_kwords=bl)
        self.archive_pt = YoutubeMonitor(db_name="FilmsAndClips_pt",
                                         min_duration=30 * 60,
                                         logger=LOG,
                                         blacklisted_kwords=bl)

    def initialize(self):
        bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips/raw/dev/bootstrap.json"
        self.archive.bootstrap_from_url(bootstrap)
        bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips_en/raw/dev/bootstrap.json"
        self.archive_en.bootstrap_from_url(bootstrap)
        bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips_es/raw/dev/bootstrap.json"
        self.archive_es.bootstrap_from_url(bootstrap)
        bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips_pt/raw/dev/bootstrap.json"
        self.archive_pt.bootstrap_from_url(bootstrap)
        bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips_it/raw/dev/bootstrap.json"
        self.archive_it.bootstrap_from_url(bootstrap)
        bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips_de/raw/dev/bootstrap.json"
        self.archive_de.bootstrap_from_url(bootstrap)
        bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips_fr/raw/dev/bootstrap.json"
        self.archive_fr.bootstrap_from_url(bootstrap)

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

        if self.lang.startswith("en"):
            pl += [{
                "title": video["title"],
                "image": video["thumbnail"],
                "match_confidence": 70,
                "media_type": MediaType.MOVIE,
                "uri": "youtube//" + video["url"],
                "playback": PlaybackType.VIDEO,
                "skill_icon": self.skill_icon,
                "bg_image": video["thumbnail"],
                "skill_id": self.skill_id
            } for video in self.archive_en.sorted_entries()][:num_entries]

        elif self.lang.startswith("pt"):
            pl += [{
                "title": video["title"],
                "image": video["thumbnail"],
                "match_confidence": 70,
                "media_type": MediaType.MOVIE,
                "uri": "youtube//" + video["url"],
                "playback": PlaybackType.VIDEO,
                "skill_icon": self.skill_icon,
                "bg_image": video["thumbnail"],
                "skill_id": self.skill_id
            } for video in self.archive_pt.sorted_entries()][:num_entries]
        elif self.lang.startswith("es"):
            pl += [{
                "title": video["title"],
                "image": video["thumbnail"],
                "match_confidence": 70,
                "media_type": MediaType.MOVIE,
                "uri": "youtube//" + video["url"],
                "playback": PlaybackType.VIDEO,
                "skill_icon": self.skill_icon,
                "bg_image": video["thumbnail"],
                "skill_id": self.skill_id
            } for video in self.archive_es.sorted_entries()][:num_entries]
        elif self.lang.startswith("fr"):
            pl += [{
                "title": video["title"],
                "image": video["thumbnail"],
                "match_confidence": 70,
                "media_type": MediaType.MOVIE,
                "uri": "youtube//" + video["url"],
                "playback": PlaybackType.VIDEO,
                "skill_icon": self.skill_icon,
                "bg_image": video["thumbnail"],
                "skill_id": self.skill_id
            } for video in self.archive_fr.sorted_entries()][:num_entries]
        elif self.lang.startswith("it"):
            pl += [{
                "title": video["title"],
                "image": video["thumbnail"],
                "match_confidence": 70,
                "media_type": MediaType.MOVIE,
                "uri": "youtube//" + video["url"],
                "playback": PlaybackType.VIDEO,
                "skill_icon": self.skill_icon,
                "bg_image": video["thumbnail"],
                "skill_id": self.skill_id
            } for video in self.archive_it.sorted_entries()][:num_entries]
        elif self.lang.startswith("de"):
            pl += [{
                "title": video["title"],
                "image": video["thumbnail"],
                "match_confidence": 70,
                "media_type": MediaType.MOVIE,
                "uri": "youtube//" + video["url"],
                "playback": PlaybackType.VIDEO,
                "skill_icon": self.skill_icon,
                "bg_image": video["thumbnail"],
                "skill_id": self.skill_id
            } for video in self.archive_de.sorted_entries()][:num_entries]

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
