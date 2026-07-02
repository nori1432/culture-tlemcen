"""
fix_images.py
Fixes places that still have old repeated images.
Uses ONLY verified Tlemcen monument categories (no general/fungi-polluted Tlemcen cat).
Downloads sequentially with rate limiting.
"""
import os, sys, time, requests

sys.path.insert(0, os.path.dirname(__file__))
IMG_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
H = {'User-Agent': 'TlemcenTourApp/1.0 (education; norichaos1@gmail.com)'}
COMMONS = 'https://commons.wikimedia.org/w/api.php'

# Only verified architecture/monument categories
ARCH_CATS = [
    'Complex_of_Sidi_Boumediene',
    'El_Mechouar_Mosque',
    'Great_Mosque_of_Tlemcen',
    'Sidi_Bel_Hasan_Mosque',
    'Tomb_of_Sidi_Boumediene',
    'Sidi_Boumediene_Mosque',
    'Agadir_Mosque',
    'Gates_in_Tlemcen',
    'Awlad_al-Imam_Mosque',
    'Bab_Zir_Mosque',
    'Mosque_of_Sidi_Abou_Ishaq_Et-Tayyar',
    'Lalla_al-Ruya_Mosque',
    'Al-Sharif_Al-Tilimsani_Mosque',
    'Madrasas_in_Tlemcen',
    'Mansourah_Mosque',
]

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')

def get_cat_file_titles(cat, limit=50):
    p = {'action':'query','list':'categorymembers','cmtitle':f'Category:{cat}',
         'cmtype':'file','cmlimit':min(limit,50),'format':'json'}
    try:
        r = requests.get(COMMONS, params=p, headers=H, timeout=15)
        members = r.json()['query']['categorymembers']
        return [m['title'] for m in members
                if any(m['title'].lower().endswith(e.lower()) for e in IMAGE_EXTS)]
    except Exception as e:
        print(f'  cat err {cat}: {e}')
        return []

def get_urls_batch(titles):
    """Resolve up to 50 File: titles to image URLs (800px thumbnails)."""
    if not titles:
        return {}
    p = {'action':'query','titles':'|'.join(titles[:50]),'prop':'imageinfo',
         'iiprop':'url','iiurlwidth':800,'format':'json'}
    try:
        r = requests.get(COMMONS, params=p, headers=H, timeout=15)
        data = r.json()
        if 'query' not in data:
            print(f'  API err: {list(data.keys())}')
            return {}
        result = {}
        for page in data['query']['pages'].values():
            title = page.get('title','')
            ii = page.get('imageinfo', [])
            if ii:
                u = ii[0].get('thumburl') or ii[0].get('url')
                if u:
                    result[title] = u
        return result
    except Exception as e:
        print(f'  batch err: {e}')
        return {}

def download_image(url, path, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=H, timeout=30, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 3000:
                with open(path, 'wb') as f:
                    f.write(r.content)
                return True
            elif r.status_code == 429:
                print(f'    rate limit, waiting 5s...')
                time.sleep(5)
            else:
                print(f'    {r.status_code} len={len(r.content)}')
                break
        except Exception as e:
            if attempt < retries-1:
                time.sleep(2)
    return False

# ── Step 1: identify old/repeated images ─────────────────────────────────
print('=== Identifying old images to replace ===')
from collections import defaultdict
size_groups = defaultdict(list)
for i in range(1, 169):
    p = os.path.join(IMG_DIR, f'place_{i}.jpg')
    if os.path.exists(p):
        sz = os.path.getsize(p)
        size_groups[sz].append(i)

# Any size group with >2 places is a duplicate batch
to_fix = set()
for sz, ids in size_groups.items():
    if len(ids) > 2:
        # Keep first 2, re-download rest
        to_fix.update(ids[2:])
        print(f'  size {sz//1024}KB: {len(ids)} dupes ({ids[:3]}...)')

print(f'\nPlaces to fix: {len(to_fix)} -> {sorted(to_fix)}')

# ── Step 2: Build clean pool from architecture categories ─────────────────
print('\n=== Building architecture image pool ===')
pool_titles = []
for cat in ARCH_CATS:
    titles = get_cat_file_titles(cat, limit=50)
    print(f'  {cat}: {len(titles)} files')
    pool_titles.extend(titles)
    time.sleep(0.4)

# De-duplicate
seen = set()
unique_titles = []
for t in pool_titles:
    if t not in seen:
        seen.add(t)
        unique_titles.append(t)
print(f'\nUnique file titles: {len(unique_titles)}')

# Resolve all to URLs
print('Resolving URLs...')
pool_urls = []
for chunk in [unique_titles[i:i+50] for i in range(0, len(unique_titles), 50)]:
    url_map = get_urls_batch(chunk)
    pool_urls.extend(url_map.values())
    time.sleep(0.5)

print(f'Resolved URLs: {len(pool_urls)}')

# ── Step 3: Assign + download for failed places ───────────────────────────
print(f'\n=== Downloading for {len(to_fix)} places ===')
places_list = sorted(to_fix)
ok = 0
fail = 0
cursor = 0

for place_id in places_list:
    if not pool_urls:
        print(f'  [{place_id:3d}] pool empty!')
        break

    dest = os.path.join(IMG_DIR, f'place_{place_id}.jpg')

    # Try up to 3 pool images until one downloads OK
    for _ in range(min(3, len(pool_urls))):
        url = pool_urls[cursor % len(pool_urls)]
        cursor += 1
        success = download_image(url, dest)
        if success:
            sz = os.path.getsize(dest) // 1024
            print(f'  [{place_id:3d}] OK {sz}KB {url[50:80]}')
            ok += 1
            break
        time.sleep(0.2)
    else:
        print(f'  [{place_id:3d}] FAIL')
        fail += 1

    time.sleep(0.3)  # rate limit between places

print(f'\nFixed: {ok}/{len(places_list)}, Failed: {fail}')

# ── Step 4: Update DB for all places ─────────────────────────────────────
print('\n=== Updating DB ===')
from app import app
from models import db, Place

with app.app_context():
    updated = 0
    for num in range(1, 169):
        p = os.path.join(IMG_DIR, f'place_{num}.jpg')
        if os.path.exists(p) and os.path.getsize(p) > 2000:
            place = Place.query.get(num)
            if place:
                place.photo_url = f'http://127.0.0.1:5000/static/images/place_{num}.jpg'
                updated += 1
    db.session.commit()
    print(f'Updated: {updated}/168')

# ── Final check ───────────────────────────────────────────────────────────
size_groups2 = defaultdict(list)
for i in range(1, 169):
    p = os.path.join(IMG_DIR, f'place_{i}.jpg')
    if os.path.exists(p):
        size_groups2[os.path.getsize(p)].append(i)

repeats = {sz: ids for sz, ids in size_groups2.items() if len(ids) > 2}
print(f'\nRemaining repeat groups: {len(repeats)}')
for sz, ids in sorted(repeats.items(), key=lambda x: -len(x[1]))[:5]:
    print(f'  {sz//1024}KB: {len(ids)} places -> {ids[:5]}')

unique_sizes = len(size_groups2)
print(f'Unique file sizes: {unique_sizes}')
print('Done.')
