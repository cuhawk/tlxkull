"""Curated whitelist of personal/research blogs from wiki/people roster.
Emits the firecrawl crawl jobs we want to run."""
import json
from pathlib import Path

# Each entry: (host_or_root_url, owner_slug, include_paths_regex_or_None, depth, limit)
JOBS = [
    # PortSwigger research blog (Kettle, Heyes, et al.) — heavy but high-signal
    ("https://portswigger.net/research", "portswigger", ["^/research/.*"], 4, 200),
    # Embrace the Red — Johann Rehberger AI red team
    ("https://embracethered.com", "embracethered", None, 4, 150),
    # Assetnote research
    ("https://blog.assetnote.io", "assetnote", None, 4, 150),
    # Orange Tsai
    ("https://blog.orange.tw", "orange-tsai", None, 4, 80),
    # zlz / Brett Buerhaus
    ("https://buer.haus", "zlz-buerhaus", None, 4, 80),
    # Sam Curry
    ("https://samcurry.net", "sam-curry", None, 4, 80),
    # Kevin Mizu
    ("https://mizu.re", "kevin-mizu", None, 4, 80),
    # Michał Bentkowski / Securitum research
    ("https://research.securitum.com", "securitum", None, 4, 80),
    # Eugene Lim / spaceraccoon
    ("https://spaceraccoon.dev", "spaceraccoon", None, 4, 80),
    # Oversecured
    ("https://blog.oversecured.com", "oversecured", None, 4, 80),
    # Gareth Heyes personal
    ("https://garethheyes.co.uk", "gareth-heyes", None, 4, 60),
    # James Kettle personal
    ("https://jameskettle.com", "james-kettle", None, 4, 60),
    # Daniel Miessler
    ("https://danielmiessler.com", "daniel-miessler", ["^/blog/.*", "^/p/.*"], 4, 100),
    # Joseph Thacker / rez0
    ("https://josephthacker.com", "rez0-thacker", None, 4, 80),
    # Corben Leo
    ("https://corben.io", "corben-leo", None, 4, 60),
    # Gal Nagli
    ("https://galnagli.com", "gal-nagli", None, 4, 60),
    # Johan Carlsson
    ("https://joaxcar.com", "johan-carlsson", None, 4, 60),
    # Matan Berson
    ("https://matanber.com", "matanber", None, 4, 60),
    # Nick Copi / 7urb0
    ("https://nickcopi.site", "nick-copi", None, 4, 60),
    # Inti De Ceukelaire
    ("https://inti.io", "inti", None, 4, 60),
    # Mathias Karlsson
    ("https://avlidienbrunn.se", "mathias-karlsson", None, 4, 60),
    # Spaceraccoon's book site (writeups)
    ("https://fromdayzerotozeroday.com", "spaceraccoon-book", None, 4, 40),
    # slonser
    ("https://blog.slonser.info", "slonser", None, 4, 60),
    # Alex Chapman
    ("https://blog.ajxchapman.com", "alex-chapman", None, 4, 60),
    # Renniepak CSP bypass research
    ("https://cspbypass.com", "renniepak-csp", None, 4, 60),
    # Daniel Thatcher
    ("https://blog.long.lat", "daniel-thatcher", None, 4, 60),
    # Matt Brown Brown Fine Security
    ("https://brownfinesecurity.com", "matt-brown", None, 4, 60),
    # jr0ch17
    ("https://blog.jr0ch17.com", "jr0ch17", None, 4, 60),
    # Sam Erb
    ("https://blog.erbbysam.com", "sam-erb", None, 4, 40),
    # Douglas Day
    ("https://dday.us", "douglas-day", None, 4, 40),
    # Gal Nagli github writeups
    ("https://naglinagli.github.io", "naglinagli-gh", None, 4, 40),
    # cablej / Jack Cable
    ("https://cablej.io", "jack-cable", None, 4, 40),
]


def main():
    Path("/tmp/personal_blog_queue.json").write_text(json.dumps(JOBS, indent=2))
    print(f"Queued {len(JOBS)} crawls")
    for j in JOBS:
        print(f"  {j[1]:25} <- {j[0]}")


if __name__ == "__main__":
    main()
