"""
migrate_to_aiven.py
Copies all data from local MySQL → Aiven MySQL.

1. Creates all tables on Aiven (db.create_all)
2. Reads every row from local MySQL
3. Inserts into Aiven (skips duplicates)

Run from the backend directory:
    python migrate_to_aiven.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

LOCAL_URL  = 'mysql+pymysql://root:@localhost:3306/tlemcen_tour'
AIVEN_URL  = 'mysql+pymysql://avnadmin:AVNS_LF_EXA92mh4DfskevxL@mysql-culture-ferhat-culture.h.aivencloud.com:16389/defaultdb'

AIVEN_SSL = {
    'ssl_disabled': False,
    'ssl_verify_cert': False,
    'ssl_verify_identity': False,
}

print('Connecting to local MySQL ...')
local_engine = create_engine(LOCAL_URL, poolclass=NullPool)

print('Connecting to Aiven MySQL ...')
aiven_engine = create_engine(
    AIVEN_URL,
    poolclass=NullPool,
    connect_args=AIVEN_SSL,
)

# ── Test both connections ─────────────────────────────────────────────────────
with local_engine.connect() as c:
    row = c.execute(text('SELECT DATABASE()')).fetchone()
    print(f'Local  DB: {row[0]}')

with aiven_engine.connect() as c:
    row = c.execute(text('SELECT DATABASE()')).fetchone()
    print(f'Aiven  DB: {row[0]}')

# ── Create schema on Aiven using the ORM models ───────────────────────────────
print('\nCreating schema on Aiven ...')
from models import db
from flask import Flask
from config import Config

# Temporarily override DATABASE_URL to point at Aiven for schema creation
os.environ['DATABASE_URL'] = AIVEN_URL

aiven_app = Flask(__name__)
aiven_app.config.from_object(Config)
db.init_app(aiven_app)

with aiven_app.app_context():
    db.create_all()
    print('Schema created (or already exists).')

# ── Helper ────────────────────────────────────────────────────────────────────
LocalSession = sessionmaker(bind=local_engine)
AivenSession = sessionmaker(bind=aiven_engine)

def migrate_table(table: str, id_col: str = 'id') -> int:
    """Copy every row of a table from local to Aiven. Returns rows inserted."""
    with local_engine.connect() as lc:
        rows = lc.execute(text(f'SELECT * FROM `{table}`')).fetchall()
        if not rows:
            print(f'  {table}: (empty)')
            return 0
        cols = lc.execute(text(f'SELECT * FROM `{table}` LIMIT 0')).keys()
        cols = list(cols)

    inserted = 0
    with aiven_engine.begin() as ac:
        # Disable FK checks during bulk load
        ac.execute(text('SET FOREIGN_KEY_CHECKS=0'))
        for row in rows:
            row_dict = dict(zip(cols, row))
            col_names = ', '.join(f'`{c}`' for c in cols)
            placeholders = ', '.join(f':{c}' for c in cols)
            sql = text(
                f'INSERT IGNORE INTO `{table}` ({col_names}) VALUES ({placeholders})'
            )
            ac.execute(sql, row_dict)
            inserted += 1
        ac.execute(text('SET FOREIGN_KEY_CHECKS=1'))

    return inserted

# ── Migration order (respects FK dependencies) ───────────────────────────────
tables = [
    'places',
    'place_translations',
    'categories',
    'qr_codes',
    'tours',
    'tour_translations',
    '`references`',   # backtick-quoted: reserved word
    'services',
]

print('\nMigrating tables ...')
total = 0
for tbl in tables:
    clean = tbl.strip('`')
    n = migrate_table(clean)
    print(f'  {clean:<25} {n:>4} rows')
    total += n

# ── Verify row counts on both ends ───────────────────────────────────────────
print('\nVerification (local vs Aiven):')
check_tables = ['places', 'place_translations', 'categories', 'qr_codes',
                'tours', 'tour_translations', 'references', 'services']

with local_engine.connect() as lc, aiven_engine.connect() as ac:
    for t in check_tables:
        local_n = lc.execute(text(f'SELECT COUNT(*) FROM `{t}`')).scalar()
        aiven_n = ac.execute(text(f'SELECT COUNT(*) FROM `{t}`')).scalar()
        status = 'OK' if local_n == aiven_n else 'MISMATCH'
        print(f'  {t:<25} local={local_n:<5} aiven={aiven_n:<5} {status}')

print(f'\nDone - {total} total rows inserted into Aiven.')
