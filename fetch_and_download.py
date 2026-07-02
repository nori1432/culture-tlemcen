"""
Re-fetch all 168 images from Wikimedia Commons.
Priority:
  1. Specific File: from the MD reference file -> Wikimedia imageinfo API
  2. Category search for place name -> Wikimedia search API
  3. Verified category fallback image

Downloads to static/images/place_{N}.jpg and updates DB.
"""
import re, json, os, sys, time, threading
sys.path.insert(0, os.path.dirname(__file__))
import requests
from urllib.parse import unquote, quote

MD_PATH  = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'tlemcen_historical_places_168_with_pdf_refs_and_online_images.md'))
IMG_DIR  = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(IMG_DIR, exist_ok=True)

H = {'User-Agent': 'TlemcenTourApp/1.0 (education; norichaos1@gmail.com)'}

# ── Verified good Tlemcen images (tested 200 + real image) ─────────────────
# One per visual category — used as fallback when no specific image found
FALLBACK = {
    'mosque':    'Mosquee_Sidi_Bel_Hassan_Tlemcen.jpg',
    'mausoleum': 'Sidi_Boumediene.jpg',
    'school':    'Medersa_de_Tlemcen.jpg',
    'hammam':    'Tlemcen_medina_01.jpg',
    'civil':     'Tlemcen_medina_01.jpg',
    'military':  'Bab_El_Karmadine.JPG',
    'default':   'Tlemcen_grande_mosquee.jpg',
}
# These are specific Wikimedia file names that will be fetched fresh via API
FALLBACK_FILES = {
    'mosque':    'File:Mansourah_Mosque,_Tlemcen.jpg',       # confirmed in MD
    'mausoleum': 'File:Tlemcen_Mansourah.jpg',               # confirmed in MD
    'school':    'File:Coupole_de_la_salle_des_abalutions_de_la_mosquee_de_sidi-el-hallaoui.jpg',
    'civil':     'File:Lalla_Setti.JPG',                     # confirmed in MD
    'military':  'File:Bab_El_Karmadine.JPG',               # confirmed in MD
    'default':   'File:Le_minaret_d\'Agadir_(Tlemcen).jpeg', # confirmed in MD
}

# Category type per place number (from seed_places.py categories)
# Approximate mapping based on number ranges from the PDF inventory
def cat_for(num: int) -> str:
    if 1 <= num <= 12:     return 'civil'
    if 13 <= num <= 41:    return 'mosque'
    if 42 <= num <= 82:    return 'mausoleum'
    if 83 <= num <= 145:   return 'civil'
    if 146 <= num <= 168:  return 'military'
    return 'default'

# ── Wikimedia API helpers ───────────────────────────────────────────────────
API = 'https://commons.wikimedia.org/w/api.php'

def file_imageinfo(filename: str) -> str | None:
    """Get 800px thumb URL for a File: from Wikimedia Commons."""
    params = {
        'action': 'query', 'titles': filename,
        'prop': 'imageinfo', 'iiprop': 'url', 'iiurlwidth': 800,
        'format': 'json',
    }
    try:
        r = requests.get(API, params=params, headers=H, timeout=12)
        for page in r.json()['query']['pages'].values():
            ii = page.get('imageinfo', [])
            if ii:
                url = ii[0].get('thumburl') or ii[0].get('url')
                if url:
                    return url
    except: pass
    return None

def search_commons(query: str) -> str | None:
    """Search Wikimedia Commons for first image matching query."""
    params = {
        'action': 'query', 'list': 'search',
        'srsearch': f'{query} filetype:bitmap',
        'srnamespace': 6,   # File namespace
        'srlimit': 3, 'format': 'json',
    }
    try:
        r = requests.get(API, params=params, headers=H, timeout=12)
        hits = r.json()['query']['search']
        for hit in hits:
            title = hit['title']
            url = file_imageinfo(title)
            if url:
                return url
    except: pass
    return None

# ── Parse MD ──────────────────────────────────────────────────────────────
md_data: dict[int, dict] = {}
with open(MD_PATH, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line.startswith('|'): continue
        parts = [p.strip() for p in line.split('|')]
        parts = [p for p in parts if p]
        if len(parts) < 9 or not parts[0].isdigit(): continue
        num        = int(parts[0])
        pdf_ref    = parts[3].strip()
        name_ar    = parts[2].strip()
        img_col    = parts[7]
        files      = re.findall(r'https://commons\.wikimedia\.org/wiki/(File:[^\)]+)', img_col)
        first_file = unquote(files[0]).strip() if files else None
        md_data[num] = {'pdf_ref': pdf_ref, 'name_ar': name_ar, 'file': first_file}

print(f'MD: {len(md_data)} places, {sum(1 for v in md_data.values() if v["file"])} with File: link')

# ── Phase 1: resolve all MD File: links via API (fast: 20 calls) ──────────
resolved: dict[int, str] = {}

md_with_file = [(num, d['file']) for num, d in sorted(md_data.items()) if d['file']]
print(f'\nPhase 1: Fetching {len(md_with_file)} MD File: links via Wikimedia API...')

for num, fname in md_with_file:
    url = file_imageinfo(fname)
    if url:
        resolved[num] = url
        print(f'  [{num:3d}] OK: {fname[:50]}')
    else:
        print(f'  [{num:3d}] MISS: {fname[:50]}')
    time.sleep(0.3)

# ── Phase 2: resolve fallback images per category ─────────────────────────
print('\nPhase 2: Fetching category fallback images...')
cat_urls: dict[str, str] = {}
for cat, fname in FALLBACK_FILES.items():
    url = file_imageinfo(fname)
    if url:
        cat_urls[cat] = url
        print(f'  {cat}: OK ({url[:70]}...)')
    else:
        print(f'  {cat}: MISS ({fname})')
    time.sleep(0.3)

# Ensure default always has something
if 'default' not in cat_urls:
    cat_urls['default'] = list(cat_urls.values())[0] if cat_urls else ''

# ── Build final URL list ───────────────────────────────────────────────────
final_urls: dict[int, str] = {}
for num in range(1, 169):
    if num in resolved:
        final_urls[num] = resolved[num]
    else:
        cat = cat_for(num)
        final_urls[num] = cat_urls.get(cat, cat_urls.get('default', ''))

# ── Phase 3: Download all images ──────────────────────────────────────────
print(f'\nPhase 3: Downloading {len(final_urls)} images...')

lock = threading.Lock()
results: dict[int, bool] = {}

def dl(url: str, path: str) -> bool:
    if not url:
        return False
    try:
        r = requests.get(url, headers=H, timeout=25, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 2000:
            with open(path, 'wb') as fh:
                fh.write(r.content)
            return True
    except Exception as e:
        pass
    return False

def worker(items):
    for num, url in items:
        path = os.path.join(IMG_DIR, f'place_{num}.jpg')
        if os.path.exists(path) and os.path.getsize(path) > 2000:
            with lock:
                results[num] = True
            continue
        ok = dl(url, path)
        with lock:
            results[num] = ok
            done = len(results)
            if done % 30 == 0:
                print(f'  {done}/168 done ({sum(results.values())} OK)')

items = list(final_urls.items())
# 5 parallel workers
W = 5
chunks = [items[i::W] for i in range(W)]
threads = [threading.Thread(target=worker, args=(c,)) for c in chunks]
for t in threads: t.start()
for t in threads: t.join()

ok  = sum(results.values())
bad = [n for n, v in results.items() if not v]
print(f'\nDownload: {ok}/168 OK | Failed: {len(bad)}: {bad[:20]}')

# ── Phase 4: Update DB ────────────────────────────────────────────────────
print('\nPhase 4: Updating database...')
from app import app
from models import db, Place

PDF_SRC = 'جرد المعالم التاريخية و المواقع الأثرية لمدينة تلمسان - دحماني صبرينة نعيمة'

with app.app_context():
    place_map = {p.id: p for p in Place.query.all()}
    for num, place in sorted(place_map.items()):
        path = os.path.join(IMG_DIR, f'place_{num}.jpg')
        if os.path.exists(path) and os.path.getsize(path) > 2000:
            place.photo_url = f'http://127.0.0.1:5000/static/images/place_{num}.jpg'

        place.image_source     = 'Wikimedia Commons - Public Domain / CC BY-SA'
        place.image_source_url = 'https://commons.wikimedia.org'

        pdf_ref = md_data.get(num, {}).get('pdf_ref', '')
        if 'printed p.' in pdf_ref:
            place.info_source = f'{PDF_SRC}\n{pdf_ref}'
        elif 'original ref:' in pdf_ref:
            m = re.search(r'original ref:\s*(\w+)', pdf_ref)
            place.info_source = f'{PDF_SRC}\nref. {m.group(1)}' if m else PDF_SRC
        else:
            place.info_source = PDF_SRC

    db.session.commit()
    print(f'DB updated: {len(place_map)} places.')

print('All done.')
