import random
from os.path import join, dirname

import requests
from json_database import JsonStorageXDG

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class FilmsAndClipsSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.MOVIE,
                                MediaType.GENERIC]
        self.skill_icon = self.default_bg = join(dirname(__file__), "ui", "filmsandclips_icon.jpg")

        self.archive = JsonStorageXDG("CultCinemaClassics", subfolder="OCP")
        self.media_type_exceptions = {
            # url 2 MediaType , if not present its a short film
        }
        super().__init__(*args, **kwargs)

    def initialize(self):
        self._sync_db()
        self.load_ocp_keywords()

    def load_ocp_keywords(self):
        titles = []
        docus = []
        actors = []
        directors = []
        genre = ["western", "horror", "thriller"]

        for url, data in self.archive.items():
            t = data["title"]

            if "Documentary" in t:
                t = t.split(" - ")[0]
                docus.append(t)
                self.media_type_exceptions[data["url"]] = MediaType.DOCUMENTARY
                continue

            t = t.replace("Full ", "").replace(" Movie HD", "").replace("English Subs", "").split(" by Film&Clips")[0]
            d = [_.strip() for _ in t.split("-") if _.strip() and _.strip() != "Movie"]
            if len(d) > 1:
                t = d[1]
                if " by " in t:
                    director = t.split(" by ")[-1]
                    directors.append(director)
                elif "with " in t:
                    actor = t.split("with ")[-1].strip(")")
                    actors.append(actor)
                elif "starring " in t:
                    actor = t.split("starring ")[-1].strip(")")
                    actors.append(actor)

            titles.append(d[0])

        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_name", titles)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_director", directors)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_actor", actors)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "film_genre", genre)
        self.register_ocp_keyword(MediaType.DOCUMENTARY,
                                  "documentary_name", docus)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_streaming_provider",
                                  ["Film and Clips", "Film&Clips", "Films and Clips", "Films&Clips"])

    def _sync_db(self):
        bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips/raw/dev/bootstrap.json"
        data = requests.get(bootstrap).json()
        self.archive.merge(data)

        if "en" in [l.split("-")[0] for l in self.native_langs]:
            bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips/raw/dev/bootstrap_en.json"
            data = requests.get(bootstrap).json()
            self.archive.merge(data)

        if "es" in [l.split("-")[0] for l in self.native_langs]:
            bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips/raw/dev/bootstrap_es.json"
            data = requests.get(bootstrap).json()
            self.archive.merge(data)

        if "pt" in [l.split("-")[0] for l in self.native_langs]:
            bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips/raw/dev/bootstrap_pt.json"
            data = requests.get(bootstrap).json()
            self.archive.merge(data)

        if "it" in [l.split("-")[0] for l in self.native_langs]:
            bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips/raw/dev/bootstrap_it.json"
            data = requests.get(bootstrap).json()
            self.archive.merge(data)

        if "de" in [l.split("-")[0] for l in self.native_langs]:
            bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips/raw/dev/bootstrap_de.json"
            data = requests.get(bootstrap).json()
            self.archive.merge(data)

        if "fr" in [l.split("-")[0] for l in self.native_langs]:
            bootstrap = "https://github.com/JarbasSkills/skill-filmsandclips/raw/dev/bootstrap_fr.json"
            data = requests.get(bootstrap).json()
            self.archive.merge(data)

        self.schedule_event(self._sync_db, random.randint(3600, 24 * 3600))

    def get_playlist(self, score=50, num_entries=50, media_type=MediaType.MOVIE):
        if media_type == MediaType.DOCUMENTARY:
            candidates = [video for video in self.archive.values()
                          if self.media_type_exceptions.get(video["url"], MediaType.MOVIE) ==
                          MediaType.DOCUMENTARY]
        else:
            candidates = [video for video in self.archive.values()
                          if video["url"] not in self.media_type_exceptions]
        pl = [{
            "title": video["title"],
            "image": video["thumbnail"],
            "match_confidence": 70,
            "media_type": media_type,
            "uri": "youtube//" + video["url"],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "bg_image": video["thumbnail"],
            "skill_id": self.skill_id
        } for video in candidates][:num_entries]

        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "bg_image": self.default_bg,
            "title": "FilmsAndClips (Movie Playlist)" if media_type == MediaType.MOVIE
                     else "FilmsAndClips (Documentary Playlist)",
            "author": "FilmsAndClips"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = 25 if media_type == MediaType.MOVIE else 0
        entities = self.ocp_voc_match(phrase)
        base_score += 30 * len(entities)

        title = entities.get("movie_name")
        actor = entities.get("movie_actor")
        director = entities.get("movie_director")
        skill = "movie_streaming_provider" in entities  # skill matched

        if skill:
            yield self.get_playlist(base_score, 25, media_type)

        if media_type == MediaType.DOCUMENTARY:
            candidates = [video for video in self.archive.values()
                          if self.media_type_exceptions.get(video["url"], MediaType.MOVIE) ==
                          MediaType.DOCUMENTARY]
        else:
            candidates = [video for video in self.archive.values()
                          if video["url"] not in self.media_type_exceptions]

        if title or actor or director:
            # only search db if user explicitly requested movies
            if title:
                base_score += 50
                candidates = [video for video in candidates
                              if title.lower() in video["title"].lower()]
            elif actor:
                base_score += 30
                candidates = [video for video in candidates
                              if actor.lower() in video["title"].lower()]
            elif director:
                base_score += 30
                candidates = [video for video in candidates
                              if director.lower() in video["title"].lower()]

            for video in candidates:
                yield {
                    "title": video["title"],
                    "artist": video["author"],
                    "match_confidence": min(100, base_score),
                    "media_type": self.media_type_exceptions.get(video["url"], MediaType.MOVIE),
                    "uri": "youtube//" + video["url"],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": video["thumbnail"],
                }

    @ocp_featured_media()
    def featured_media(self):
        return self.get_playlist()['playlist']


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = FilmsAndClipsSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_db("a movie by Piero Pierotti", MediaType.MOVIE):
        print(r)
        # {'title': "L'Arciere Nero - un Film di Piero Pierotti by Film&Clips", 'artist': 'Film&Clips', 'match_confidence': 85, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=OtwJctovncM', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/OtwJctovncM/sddefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/OtwJctovncM/sddefault.jpg'}
        # {'title': 'The Black Archer - Full Movie directed by Piero Pierotti - by Film&Clips Free Movies', 'artist': 'Film&Clips Free Movies', 'match_confidence': 85, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=4gH0iYVEq4g', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/4gH0iYVEq4g/sddefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/4gH0iYVEq4g/sddefault.jpg'}

    for r in s.search_db("George Hilton", MediaType.MOVIE):
        print(r)
        # {'title': 'The Two Faces of Fear - starring George Hilton - Full Movie by Film&Clips Free Movies', 'artist': 'Film&Clips Free Movies', 'match_confidence': 85, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=um3mXnGHjqQ', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/um3mXnGHjqQ/sddefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/um3mXnGHjqQ/sddefault.jpg'}
