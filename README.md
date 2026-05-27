# Wowhead Scraper

This project targets to scrape the [Wowhead](https://classic.wowhead.com) website and extract information about NPCs, quests, items, objects and experience points (XP). These information are primarily used for localization of the [Questie Addon](https://github.com/AeroScripts/QuestieDev/).

## How to use

### Install requirements

You will need Python to run any part of this project and the modules can be installed using the `requirements.txt`:

`pip install -r requirements.txt`

### Running the scraper

Currently this project can only be used via command line:

`python runner.py`

The available parameters are:

| Parameter         | Type  | Description                          | Possible values                                | Default |
|-------------------|-------|--------------------------------------|------------------------------------------------|---------|
| `-l`, `--lang`    | `str` | The language you want to scrape.     | `en`, `de`, `fr`, `es`, `ru`, `cn`, `pt`, `ko` | `en`    |
| `-t`, `--target`  | `str` | The target you want to scrape.       | `npc`, `quest`, `item`, `object`, `xp`         | `npc`   |
| `-v`, `--version` | `str` | The game version you want to scrape. | `classic`, `tbc`, `wotlk`, `mop`               | `wotlk` |
| `-c`, `--concurrent` | `int` | Number of concurrent requests.     | Any positive integer                            | `3`     |
| `-d`, `--delay`   | `float` | Download delay between requests.  | Any positive number (seconds)                   | `2.0`   |

### Usage examples

```bash
# Scrape all WotLK objects in Chinese (3 concurrent, 2s delay):
python runner.py -t object -v wotlk -l cn

# Slow scraping for rate-limited connections (1 concurrent, 10s delay):
python runner.py -t quest -v mop -l cn -c 1 -d 10

# Fast scraping (5 concurrent, 1s delay):
python runner.py -t item -v wotlk -l en -c 5 -d 1
```
