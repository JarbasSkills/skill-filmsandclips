import json
import shutil
from os.path import dirname, isfile

from youtube_archivist import YoutubeMonitor

bl = ["trailer", "teaser", "movie scene",
      "movie clip", "behind the scenes",
      "Movie Preview", "Clip #",
      "soundtrack", " OST", "opening theme"]
archive = YoutubeMonitor(db_name="FilmsAndClips",
                         min_duration=30 * 60,
                         blacklisted_kwords=bl)
archive_en = YoutubeMonitor(db_name="FilmsAndClips_en",
                            min_duration=30 * 60,
                            blacklisted_kwords=bl)
archive_es = YoutubeMonitor(db_name="FilmsAndClips_es",
                            min_duration=30 * 60,
                            blacklisted_kwords=bl)
archive_it = YoutubeMonitor(db_name="FilmsAndClips_it",
                            min_duration=30 * 60,
                            blacklisted_kwords=bl)
archive_de = YoutubeMonitor(db_name="FilmsAndClips_de",
                            min_duration=30 * 60,
                            blacklisted_kwords=bl)
archive_fr = YoutubeMonitor(db_name="FilmsAndClips_fr",
                            min_duration=30 * 60,
                            blacklisted_kwords=bl)
archive_pt = YoutubeMonitor(db_name="FilmsAndClips_pt",
                            min_duration=30 * 60,
                            blacklisted_kwords=bl)

# load previous cache
cache_file = f"{dirname(dirname(__file__))}/bootstrap.json"
cache_file_en = f"{dirname(dirname(__file__))}/bootstrap_en.json"
cache_file_pt = f"{dirname(dirname(__file__))}/bootstrap_pt.json"
cache_file_fr = f"{dirname(dirname(__file__))}/bootstrap_fr.json"
cache_file_es = f"{dirname(dirname(__file__))}/bootstrap_es.json"
cache_file_it = f"{dirname(dirname(__file__))}/bootstrap_it.json"
cache_file_de = f"{dirname(dirname(__file__))}/bootstrap_de.json"


if isfile(cache_file):
    try:
        with open(cache_file) as f:
            data = json.load(f)
            archive.db.update(data)
            archive.db.store()
    except:
        pass  # corrupted for some reason

    shutil.rmtree(cache_file, ignore_errors=True)

for url in [
    "https://www.youtube.com/c/FilmandClips"
]:
    # parse new vids
    archive.parse_videos(url)

for url in [
    "https://www.youtube.com/channel/UCbRPdPJpFz4f4pHeIhEck2w"
]:
    # parse new vids
    archive_en.parse_videos(url)

for url in [
    "https://www.youtube.com/channel/UCwOmaHmbjx5J_jG5IAg2Eqw"
]:
    # parse new vids
    archive_fr.parse_videos(url)

for url in [
    "https://www.youtube.com/channel/UCcG2X4bDgt1qbaKKlcQTXpg"
]:
    # parse new vids
    archive_pt.parse_videos(url)

for url in [
    "https://www.youtube.com/channel/UCZl0iSBsqAiY59Ni_0vRVfw"
]:
    # parse new vids
    archive_de.parse_videos(url)

for url in [
    "https://www.youtube.com/channel/UCGoazA0Z4aoBccf3cdrBRfA"
]:
    # parse new vids
    archive_it.parse_videos(url)

for url in [
    "https://www.youtube.com/channel/UCO2thUSgz78cRlAVW5iP3pw"
]:
    # parse new vids
    archive_es.parse_videos(url)

# save bootstrap cache
shutil.copy(archive.db.path, cache_file)
shutil.copy(archive_en.db.path, cache_file_en)
shutil.copy(archive_es.db.path, cache_file_es)
shutil.copy(archive_de.db.path, cache_file_de)
shutil.copy(archive_it.db.path, cache_file_it)
shutil.copy(archive_pt.db.path, cache_file_pt)
shutil.copy(archive_fr.db.path, cache_file_fr)
