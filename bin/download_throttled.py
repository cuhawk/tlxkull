#!/usr/bin/env python3
"""Throttled parallel downloader: respects max_rps, writes files + sourcemap probes."""
import sys, os, time, urllib.parse, urllib.request, ssl, json, hashlib, threading, queue, re

URLS_FILE = sys.argv[1]
OUT_DIR = sys.argv[2]
MAX_RPS = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5

FILES_DIR = os.path.join(OUT_DIR, "_files")
MAPS_DIR = os.path.join(OUT_DIR, "_maps")
LOG = os.path.join(OUT_DIR, "_log", "download.jsonl")
os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(MAPS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def safe_name(url):
    h = hashlib.sha1(url.encode()).hexdigest()[:10]
    p = urllib.parse.urlparse(url)
    base = (p.netloc + p.path).replace("/", "__")
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    return f"{base}__{h}"

def fetch(url, dest, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
            return r.status, len(data)
    except urllib.error.HTTPError as e:
        return e.code, 0
    except Exception as e:
        return -1, 0

interval = 1.0 / MAX_RPS
last_t = [0]
lock = threading.Lock()
log_lock = threading.Lock()

def throttle():
    with lock:
        now = time.time()
        wait = interval - (now - last_t[0])
        if wait > 0:
            time.sleep(wait)
        last_t[0] = time.time()

def log(rec):
    with log_lock:
        with open(LOG, "a") as f:
            f.write(json.dumps(rec) + "\n")

with open(URLS_FILE) as f:
    urls = [u.strip() for u in f if u.strip()]

print(f"downloading {len(urls)} JS + probing sourcemaps @ {MAX_RPS} rps")
ok = 0; map_ok = 0; failed = 0
for i, url in enumerate(urls):
    throttle()
    name = safe_name(url)
    dest = os.path.join(FILES_DIR, name + ".js")
    code, size = fetch(url, dest)
    log({"n": i+1, "url": url, "file": dest, "code": code, "size": size})
    if code == 200 and size > 0:
        ok += 1
    else:
        failed += 1
        if os.path.exists(dest):
            os.remove(dest)

    # sourcemap probe (separate request, half-budget)
    map_url = re.sub(r"(\.js)(\?|$)", r".js.map\2", url)
    if map_url != url:
        throttle()
        map_dest = os.path.join(MAPS_DIR, name + ".js.map")
        mcode, msize = fetch(map_url, map_dest, timeout=15)
        log({"n": i+1, "map": map_url, "code": mcode, "size": msize})
        if mcode == 200 and msize > 0:
            map_ok += 1
        else:
            if os.path.exists(map_dest):
                os.remove(map_dest)

    if (i+1) % 10 == 0:
        print(f"  {i+1}/{len(urls)} ok={ok} maps={map_ok} failed={failed}")

print(f"DONE total={len(urls)} files_ok={ok} maps_ok={map_ok} failed={failed}")
