"""Fix the 37 remaining missing images and update DB."""
import os, sys, time, requests
sys.path.insert(0, os.path.dirname(__file__))

IMG_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
H = {'User-Agent': 'TlemcenTourApp/1.0 (education; norichaos1@gmail.com)'}
API = 'https://commons.wikimedia.org/w/api.php'

def file_url(fname):
    p = {'action': 'query', 'titles': fname, 'prop': 'imageinfo',
         'iiprop': 'url', 'iiurlwidth': 800, 'format': 'json'}
    try:
        r = requests.get(API, params=p, headers=H, timeout=12)
        for page in r.json()['query']['pages'].values():
            ii = page.get('imageinfo', [])
            if ii:
                return ii[0].get('thumburl') or ii[0].get('url')
    except Exception as e:
        print(f'  API err: {e}')
    return None

def cat_for(num):
    if 13 <= num <= 41:  return 'mosque'
    if 42 <= num <= 82:  return 'mausoleum'
    if 146 <= num <= 168: return 'military'
    return 'civil'

# Fetch verified fallback URLs
print('Fetching category fallback URLs...')
fallbacks = {
    'mosque':    file_url('File:Mansourah_Mosque,_Tlemcen.jpg'),
    'mausoleum': file_url('File:Tlemcen_Mansourah.jpg'),
    'civil':     file_url('File:Lalla_Setti.JPG'),
    'military':  file_url('File:Bab_El_Karmadine.JPG'),
}
fallbacks['default'] = file_url("File:Le_minaret_d'Agadir_(Tlemcen).jpeg")
for k, v in fallbacks.items():
    print(f'  {k}: {"OK" if v else "MISS"} {(v or "")[:60]}')
time.sleep(0.5)

# Find missing
missing = []
for i in range(1, 169):
    path = os.path.join(IMG_DIR, f'place_{i}.jpg')
    if not os.path.exists(path) or os.path.getsize(path) < 2000:
        missing.append(i)
print(f'\nMissing images: {len(missing)} -> {missing}')

# Download
ok = 0
for num in missing:
    cat = cat_for(num)
    url = fallbacks.get(cat) or fallbacks.get('default')
    if not url:
        print(f'  [{num}] no URL for cat {cat}')
        continue
    path = os.path.join(IMG_DIR, f'place_{num}.jpg')
    try:
        r = requests.get(url, headers=H, timeout=20, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 2000:
            with open(path, 'wb') as fh:
                fh.write(r.content)
            ok += 1
        else:
            print(f'  [{num}] {r.status_code} len={len(r.content)}')
    except Exception as e:
        print(f'  [{num}] ERR: {e}')
    time.sleep(0.05)

print(f'\nFixed: {ok}/{len(missing)}')

# Update DB
from app import app
from models import db, Place

with app.app_context():
    places = {p.id: p for p in Place.query.all()}
    updated = 0
    for num, place in places.items():
        path = os.path.join(IMG_DIR, f'place_{num}.jpg')
        if os.path.exists(path) and os.path.getsize(path) > 2000:
            place.photo_url = f'http://127.0.0.1:5000/static/images/place_{num}.jpg'
            updated += 1
    db.session.commit()
    print(f'DB updated: {updated}/168 places with local images')

total = (get := lambda: sum(1 for i in range(1, 169) if os.path.exists(os.path.join(IMG_DIR, f'place_{i}.jpg')) and os.path.getsize(os.path.join(IMG_DIR, f'place_{i}.jpg')) > 2000))()
print(f'Total valid images on disk: {total}/168')
