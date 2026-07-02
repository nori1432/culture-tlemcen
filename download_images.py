"""
Fast image downloader: uses Wikimedia Special:FilePath redirects (no API calls).
Sources priority per place:
  1. Specific File: link from the MD reference file
  2. Fallback URL from images_result.json
Skips already-downloaded images.
Updates DB: photo_url -> local Flask URL, info_source -> PDF page ref.
Run from backend/: python download_images.py
"""

import re
import json
import time
import os
import sys
import threading
sys.path.insert(0, os.path.dirname(__file__))

import requests
from urllib.parse import unquote

MD_PATH   = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'tlemcen_historical_places_168_with_pdf_refs_and_online_images.md'))
IMG_DIR   = os.path.join(os.path.dirname(__file__), 'static', 'images')
JSON_PATH = os.path.join(os.path.dirname(__file__), 'images_result.json')

os.makedirs(IMG_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'TlemcenTourApp/1.0 (educational tourism; norichaos1@gmail.com)',
}

# ── Load fallback image URLs ───────────────────────────────────────────────
with open(JSON_PATH, encoding='utf-8') as f:
    fallback_urls: dict[int, str] = {int(k): v for k, v in json.load(f).items()}

# ── Generic Tlemcen fallback ───────────────────────────────────────────────
GENERIC = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Tlemcen_el_mechouar.jpg/800px-Tlemcen_el_mechouar.jpg'


def file_to_url(filename: str) -> str:
    """Convert Wikimedia filename to 800px Special:FilePath URL (follows redirect)."""
    clean = filename.replace(' ', '_')
    return f'https://commons.wikimedia.org/wiki/Special:FilePath/{clean}?width=800'


def download(url: str, path: str) -> bool:
    """Download url to path, follow redirects. Returns True on success."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        if r.status_code == 200 and ('image' in ct or r.headers.get('Content-Length', '0') != '0'):
            data = b''.join(r.iter_content(8192))
            if len(data) > 2000:
                with open(path, 'wb') as fh:
                    fh.write(data)
                return True
    except Exception as e:
        print(f'    ERR {url[:60]}: {e}')
    return False


# ── Parse MD table ─────────────────────────────────────────────────────────
md_data: dict[int, dict] = {}

with open(MD_PATH, encoding='utf-8') as f:
    md_content = f.read()

for line in md_content.split('\n'):
    line = line.strip()
    if not line.startswith('|'):
        continue
    parts = [p.strip() for p in line.split('|')]
    parts = [p for p in parts if p != '']
    if len(parts) < 9 or not parts[0].isdigit():
        continue

    num        = int(parts[0])
    pdf_ref    = parts[3].strip()
    img_col    = parts[7]

    # Extract first File: link
    file_names = re.findall(r'https://commons\.wikimedia\.org/wiki/File:([^\)]+)', img_col)
    first_file = unquote(file_names[0]).strip() if file_names else None

    md_data[num] = {'pdf_ref': pdf_ref, 'file_name': first_file}

with_file = sum(1 for v in md_data.values() if v['file_name'])
print(f'MD parsed: {len(md_data)} places | {with_file} with specific File: link | {len(md_data)-with_file} using fallback')

# ── Build download list ────────────────────────────────────────────────────
tasks: list[tuple[int, str]] = []

for num in sorted(md_data.keys()):
    path = os.path.join(IMG_DIR, f'place_{num}.jpg')
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        tasks.append((num, ''))  # already exists
        continue

    file_name = md_data[num]['file_name']
    if file_name:
        url = file_to_url(file_name)
    else:
        url = fallback_urls.get(num, GENERIC)
    tasks.append((num, url))

already = sum(1 for _, u in tasks if u == '')
to_download = len(tasks) - already
print(f'Already downloaded: {already} | Need to download: {to_download}')

# ── Download with threading (5 workers) ───────────────────────────────────
lock = threading.Lock()
results: dict[int, bool] = {}

def worker(items):
    for num, url in items:
        if url == '':
            with lock:
                results[num] = True
            continue
        path = os.path.join(IMG_DIR, f'place_{num}.jpg')
        ok = download(url, path)
        if not ok and md_data[num]['file_name']:
            # Try fallback url from images_result.json
            fb = fallback_urls.get(num, GENERIC)
            ok = download(fb, path)
        if not ok:
            ok = download(GENERIC, path)
        with lock:
            results[num] = ok
            total = len(results)
            if total % 20 == 0:
                done = sum(1 for v in results.values() if v)
                print(f'  Progress: {total}/168 processed, {done} OK')

NUM_WORKERS = 6
chunk = [t for t in tasks if t[1] != '']
# Pre-fill already-done
for num, url in tasks:
    if url == '':
        results[num] = True

size = max(1, len(chunk) // NUM_WORKERS)
chunks = [chunk[i:i+size] for i in range(0, len(chunk), size)]

threads = [threading.Thread(target=worker, args=(c,)) for c in chunks]
for t in threads:
    t.start()
for t in threads:
    t.join()

ok_count = sum(1 for v in results.values() if v)
failed   = [num for num, ok in results.items() if not ok]
print(f'\nDownload complete: {ok_count}/168 OK | Failed: {len(failed)}: {failed}')

# ── Update DB ──────────────────────────────────────────────────────────────
from app import app
from models import db, Place

PDF_TITLE = 'جرد المعالم التاريخية و المواقع الأثرية لمدينة تلمسان - دحماني صبرينة نعيمة'

with app.app_context():
    place_map = {p.id: p for p in Place.query.all()}
    updated = 0
    for num in sorted(md_data.keys()):
        place = place_map.get(num)
        if not place:
            continue

        local_path = os.path.join(IMG_DIR, f'place_{num}.jpg')
        if os.path.exists(local_path) and os.path.getsize(local_path) > 2000:
            place.photo_url = f'http://127.0.0.1:5000/static/images/place_{num}.jpg'
        # else keep existing

        place.image_source     = 'Wikimedia Commons - Public Domain / CC BY-SA'
        place.image_source_url = 'https://commons.wikimedia.org'

        pdf_ref = md_data.get(num, {}).get('pdf_ref', '')
        if pdf_ref and 'printed p.' in pdf_ref:
            place.info_source = f'{PDF_TITLE}\n{pdf_ref}'
        elif pdf_ref and 'original ref:' in pdf_ref:
            m = re.search(r'original ref:\s*(\w+)', pdf_ref)
            place.info_source = f'{PDF_TITLE}\nref. {m.group(1)}' if m else PDF_TITLE
        else:
            place.info_source = PDF_TITLE
        updated += 1

    db.session.commit()
    print(f'DB updated: {updated} places.')

print('Done.')
