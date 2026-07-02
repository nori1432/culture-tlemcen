"""
copy_images.py
Copies downloaded place images from static/images/ to public/images/
so Vercel can serve them as static CDN files.

Run once before deploying:
    python copy_images.py
"""
import os
import shutil

SRC = os.path.join(os.path.dirname(__file__), 'static', 'images')
DST = os.path.join(os.path.dirname(__file__), 'public', 'images')

os.makedirs(DST, exist_ok=True)

copied = skipped = missing = 0
for i in range(1, 169):
    name = f'place_{i}.jpg'
    src_path = os.path.join(SRC, name)
    dst_path = os.path.join(DST, name)
    if not os.path.exists(src_path):
        print(f'  MISSING  {name}')
        missing += 1
        continue
    if os.path.exists(dst_path) and os.path.getsize(dst_path) == os.path.getsize(src_path):
        skipped += 1
        continue
    shutil.copy2(src_path, dst_path)
    copied += 1

total = os.path.getsize(DST) if os.path.isfile(DST) else sum(
    os.path.getsize(os.path.join(DST, f)) for f in os.listdir(DST)
) / (1024 * 1024)

print(f'\nDone — copied: {copied}, skipped (unchanged): {skipped}, missing: {missing}')
print(f'public/images/ now has {len(os.listdir(DST))} files')
