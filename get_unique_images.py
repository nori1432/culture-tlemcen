"""
get_unique_images.py
Fetches a unique image for each of the 168 Tlemcen places.
Strategy (in order of priority):
  1. Specific Wikimedia File: link (from MD analysis)
  2. Image from the place's assigned Commons category
  3. Wikipedia EN/FR page image (search by name)
  4. General Tlemcen image pool (rotated, no repeats)
"""
import os, sys, time, requests, re
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))
IMG_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(IMG_DIR, exist_ok=True)

H = {'User-Agent': 'TlemcenTourApp/1.0 (education; norichaos1@gmail.com)'}
COMMONS = 'https://commons.wikimedia.org/w/api.php'
WP_EN   = 'https://en.wikipedia.org/w/api.php'
WP_FR   = 'https://fr.wikipedia.org/w/api.php'

# ── 1. Specific File: links per place (from MD analysis) ─────────────────
SPECIFIC_FILES = {
    2:   'File:Lalla_Setti.JPG',
    3:   "File:Le_minaret_d'Agadir_(Tlemcen).jpeg",
    5:   'File:Mansourah_Mosque,_Tlemcen.jpg',
    13:  "File:Le_minaret_d'Agadir_(Tlemcen).jpeg",
    21:  'File:Tlemcen_Mosque_Sidi_El_Benna.png',
    36:  'File:El_mechouar_palace_in_Tlemcen.jpg',
    38:  'File:Mansourah_Mosque,_Tlemcen.jpg',
    78:  'File:Lalla_Setti.JPG',
    88:  'File:El_mechouar_palace_in_Tlemcen.jpg',
    146: "File:Le_minaret_d'Agadir_(Tlemcen).jpeg",
    151: 'File:Mansourah_Mosque,_Tlemcen.jpg',
    152: "File:Le_minaret_d'Agadir_(Tlemcen).jpeg",
    153: "File:Le_minaret_d'Agadir_(Tlemcen).jpeg",
    155: "File:Le_minaret_d'Agadir_(Tlemcen).jpeg",
    159: 'File:Tlemcen_Mansourah.jpg',
    161: 'File:Bab_El_Karmadine.JPG',
    162: 'File:Bab_El_Khemis_(Tlemcen).jpg',
    167: 'File:El_mechouar_palace_in_Tlemcen.jpg',
}

# ── 2. Category assignments per place (from MD analysis) ─────────────────
CATEGORY_MAP = {
    6:   'Complex_of_Sidi_Boumediene',
    7:   'Sidi_El_Haloui_Mosque',
    14:  'Sidi_El_Haloui_Mosque',
    17:  'Sidi_Bel_Hasan_Mosque',
    18:  'Bab_Zir_Mosque',
    22:  'Great_Mosque_of_Tlemcen',
    25:  'Sidi_Bel_Hasan_Mosque',
    26:  'Lalla_al-Ruya_Mosque',
    31:  'Awlad_al-Imam_Mosque',
    33:  'Al-Sharif_Al-Tilimsani_Mosque',
    40:  'Mosque_of_Sidi_Abou_Ishaq_Et-Tayyar',
    41:  'Sidi_Boumediene_Mosque',
    47:  'Sidi_El_Haloui_Mosque',
    48:  'Sidi_El_Haloui_Mosque',
    49:  'Sidi_Bel_Hasan_Mosque',
    55:  'Sidi_Bel_Hasan_Mosque',
    60:  'Tomb_of_Sidi_Boumediene',
    65:  'Mosque_of_Sidi_Abou_Ishaq_Et-Tayyar',
    72:  'Complex_of_Sidi_Boumediene',
    74:  'Complex_of_Sidi_Boumediene',
    80:  'Madrasas_in_Tlemcen',
    81:  'Awlad_al-Imam_Mosque',
    82:  'Sidi_Bel_Hasan_Mosque',
    103: 'Agadir_Mosque',
    114: 'Complex_of_Sidi_Boumediene',
    116: 'Sidi_El_Haloui_Mosque',
    120: 'Mosque_of_Sidi_Abou_Ishaq_Et-Tayyar',
    121: 'Complex_of_Sidi_Boumediene',
    122: 'Complex_of_Sidi_Boumediene',
    124: 'Al-Sharif_Al-Tilimsani_Mosque',
    133: 'Awlad_al-Imam_Mosque',
    140: 'Agadir_Mosque',
    167: 'El_Mechouar_Mosque',
}

# ── Helpers ───────────────────────────────────────────────────────────────
def get_file_url(fname):
    """Resolve a single File: title to a thumb URL via Wikimedia API."""
    p = {'action':'query','titles':fname,'prop':'imageinfo',
         'iiprop':'url','iiurlwidth':800,'format':'json'}
    try:
        r = requests.get(COMMONS, params=p, headers=H, timeout=12)
        for page in r.json()['query']['pages'].values():
            ii = page.get('imageinfo', [])
            if ii:
                return ii[0].get('thumburl') or ii[0].get('url')
    except Exception as e:
        print(f'  file_url err {fname}: {e}')
    return None

def get_cat_file_urls(cat, limit=40):
    """Fetch up to `limit` image URLs from a Commons category (images only)."""
    IMAGE_EXTS = ('.jpg','.jpeg','.png','.JPG','.JPEG','.PNG')
    # Step 1: get file titles from category
    p = {'action':'query','list':'categorymembers','cmtitle':f'Category:{cat}',
         'cmtype':'file','cmlimit':min(limit, 50),'format':'json'}
    try:
        r = requests.get(COMMONS, params=p, headers=H, timeout=12)
        members = r.json()['query']['categorymembers']
    except Exception as e:
        print(f'  cat err {cat}: {e}')
        return []

    titles = [m['title'] for m in members
              if any(m['title'].lower().endswith(ext.lower()) for ext in IMAGE_EXTS)]
    if not titles:
        return []

    # Step 2: batch-resolve titles to URLs (up to 50 at once)
    urls = []
    for chunk in [titles[i:i+50] for i in range(0, len(titles), 50)]:
        p2 = {'action':'query','titles':'|'.join(chunk),'prop':'imageinfo',
              'iiprop':'url','iiurlwidth':800,'format':'json'}
        try:
            r2 = requests.get(COMMONS, params=p2, headers=H, timeout=15)
            for page in r2.json()['query']['pages'].values():
                ii = page.get('imageinfo', [])
                if ii:
                    u = ii[0].get('thumburl') or ii[0].get('url')
                    if u:
                        urls.append(u)
            time.sleep(0.3)
        except Exception as e:
            print(f'  batch err: {e}')
    return urls

def search_wikipedia_image(name, lang='en'):
    """Search Wikipedia for a place name and return its lead image URL."""
    api = WP_EN if lang == 'en' else WP_FR
    try:
        r = requests.get(api, params={
            'action':'query','list':'search',
            'srsearch':f'{name} Tlemcen Algeria','srlimit':3,'format':'json'
        }, headers=H, timeout=8)
        results = r.json()['query']['search']
        if not results:
            return None
        title = results[0]['title']
        r2 = requests.get(api, params={
            'action':'query','titles':title,'prop':'pageimages',
            'pithumbsize':800,'format':'json'
        }, headers=H, timeout=8)
        for page in r2.json()['query']['pages'].values():
            t = page.get('thumbnail', {})
            if t.get('source'):
                return t['source']
    except Exception:
        pass
    return None

def download_image(url, dest_path):
    """Download image, return True if saved successfully (>2KB)."""
    try:
        r = requests.get(url, headers=H, timeout=25, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 2000:
            with open(dest_path, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f'  download err: {e}')
    return False

# ── Step 1: Resolve specific File: links ─────────────────────────────────
print('=== Step 1: Resolving specific File: links ===')
specific_urls = {}
unique_files = list(set(SPECIFIC_FILES.values()))
for fname in unique_files:
    url = get_file_url(fname)
    specific_urls[fname] = url
    print(f'  {fname}: {"OK" if url else "MISS"}')
    time.sleep(0.2)

# ── Step 2: Fetch category image pools ───────────────────────────────────
print('\n=== Step 2: Fetching category image pools ===')
all_cats = set(CATEGORY_MAP.values())
# Add general pool categories
POOL_CATS = [
    'Tlemcen',
    'Architecture_in_Tlemcen',
    'Great_Mosque_of_Tlemcen',
    'Old_city_of_Tlemcen',
    'Hammam_in_Algeria',
    'Gates_in_Tlemcen',
    'Medieval_architecture_in_Algeria',
]
cat_pools = {}  # cat -> [url, url, ...]
for cat in list(all_cats) + POOL_CATS:
    if cat in cat_pools:
        continue
    print(f'  Fetching {cat}...', end=' ')
    urls = get_cat_file_urls(cat, limit=40)
    cat_pools[cat] = urls
    print(f'{len(urls)} images')
    time.sleep(0.5)

# Build global pool (de-duplicated)
global_pool = []
seen_pool = set()
for cat in POOL_CATS:
    for u in cat_pools.get(cat, []):
        if u not in seen_pool:
            seen_pool.add(u)
            global_pool.append(u)

print(f'\nGlobal pool: {len(global_pool)} unique images')

# ── Step 3: Fetch place names from Flask API ─────────────────────────────
print('\n=== Step 3: Fetching place names ===')
try:
    r = requests.get('http://127.0.0.1:5000/api/places?lang=en', timeout=15)
    places_data = {p['id']: p['name']['en'] for p in r.json()}
    print(f'  Got {len(places_data)} place names')
except Exception as e:
    print(f'  Failed to get place names: {e}')
    places_data = {}

# ── Step 4: Build URL assignment per place ───────────────────────────────
print('\n=== Step 4: Assigning URLs to places ===')
cat_cursors = {cat: 0 for cat in cat_pools}  # rotating index per category
pool_cursor = 0
used_urls = set()
assignment = {}  # place_id -> url

def next_cat_url(cat):
    """Get next unique URL from a category pool."""
    pool = cat_pools.get(cat, [])
    if not pool:
        return None
    # Try to find an unused URL, allow reuse if exhausted
    start = cat_cursors[cat]
    for _ in range(len(pool)):
        url = pool[cat_cursors[cat] % len(pool)]
        cat_cursors[cat] += 1
        if url not in used_urls:
            return url
    # All used - just return next
    url = pool[cat_cursors[cat] % len(pool)]
    cat_cursors[cat] += 1
    return url

def next_pool_url():
    """Get next unique URL from general pool."""
    global pool_cursor
    if not global_pool:
        return None
    for _ in range(len(global_pool)):
        url = global_pool[pool_cursor % len(global_pool)]
        pool_cursor += 1
        if url not in used_urls:
            return url
    url = global_pool[pool_cursor % len(global_pool)]
    pool_cursor += 1
    return url

for place_id in range(1, 169):
    url = None
    source = ''

    # Priority 1: specific file
    if place_id in SPECIFIC_FILES:
        fname = SPECIFIC_FILES[place_id]
        url = specific_urls.get(fname)
        source = 'specific-file'

    # Priority 2: category pool
    if not url and place_id in CATEGORY_MAP:
        cat = CATEGORY_MAP[place_id]
        url = next_cat_url(cat)
        source = f'cat:{cat}'

    # Priority 3: Wikipedia EN/FR search
    if not url:
        place_data = places_data.get(place_id)
        if place_data:
            url = search_wikipedia_image(place_data, 'en')
            if url:
                source = 'wp-en'
            else:
                url = search_wikipedia_image(place_data, 'fr')
                if url:
                    source = 'wp-fr'
            if url:
                time.sleep(0.2)

    # Priority 4: general pool
    if not url:
        url = next_pool_url()
        source = 'pool'

    if url:
        used_urls.add(url)
        assignment[place_id] = url
        print(f'  [{place_id:3d}] {source}: {url[:70]}')
    else:
        print(f'  [{place_id:3d}] NO URL FOUND')

print(f'\nAssigned: {len(assignment)}/168')

# ── Step 5: Download images in parallel ──────────────────────────────────
print('\n=== Step 5: Downloading images ===')
ok = 0
fail = 0

def download_task(args):
    place_id, url = args
    path = os.path.join(IMG_DIR, f'place_{place_id}.jpg')
    success = download_image(url, path)
    return place_id, success

tasks = [(pid, url) for pid, url in assignment.items()]
with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(download_task, t): t[0] for t in tasks}
    for future in as_completed(futures):
        pid, success = future.result()
        if success:
            ok += 1
            sz = os.path.getsize(os.path.join(IMG_DIR, f'place_{pid}.jpg')) // 1024
            print(f'  [{pid:3d}] OK {sz}KB')
        else:
            fail += 1
            print(f'  [{pid:3d}] FAIL')

print(f'\nDownloaded: {ok}/{len(tasks)}, Failed: {fail}')

# ── Step 6: Update DB ─────────────────────────────────────────────────────
print('\n=== Step 6: Updating DB ===')
from app import app
from models import db, Place

with app.app_context():
    updated = 0
    for num in range(1, 169):
        path = os.path.join(IMG_DIR, f'place_{num}.jpg')
        if os.path.exists(path) and os.path.getsize(path) > 2000:
            place = Place.query.get(num)
            if place:
                place.photo_url = f'http://127.0.0.1:5000/static/images/place_{num}.jpg'
                updated += 1
    db.session.commit()
    print(f'Updated: {updated}/168 places in DB')

# ── Final check ───────────────────────────────────────────────────────────
valid = sum(1 for i in range(1, 169)
            if os.path.exists(os.path.join(IMG_DIR, f'place_{i}.jpg'))
            and os.path.getsize(os.path.join(IMG_DIR, f'place_{i}.jpg')) > 2000)
print(f'Valid images on disk: {valid}/168')

# Check variety (unique file sizes as proxy)
sizes = {}
for i in range(1, 169):
    p = os.path.join(IMG_DIR, f'place_{i}.jpg')
    if os.path.exists(p):
        sz = os.path.getsize(p)
        sizes[sz] = sizes.get(sz, 0) + 1
repeats = {sz: cnt for sz, cnt in sizes.items() if cnt > 1}
print(f'Unique file sizes: {len(sizes)} (repeated sizes: {len(repeats)})')
print('Done.')
