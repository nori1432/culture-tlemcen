"""
Tlemcen Smart Tour — Flask API Backend
Serves place data, QR resolution, categories, and tours.
Flutter connects here; Flask connects to MySQL. Flutter never touches MySQL directly.
"""

import os
import re
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from config import Config
from models import db, Place, PlaceTranslation, Category, QRCode, Tour, TourTranslation, Reference

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)


def _resolve_photo(url: str) -> str:
    """
    Rewrite a stored place_N.jpg URL to use IMAGE_BASE_URL in production.
    Wikimedia / other external URLs are returned unchanged.
    """
    base = app.config.get('IMAGE_BASE_URL', '').rstrip('/')
    if base and url and re.search(r'place_\d+\.jpg$', url):
        filename = url.rsplit('/', 1)[-1]
        return f"{base}/{filename}"
    return url or ''


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'app': 'Tlemcen Smart Tour API'})


@app.route('/static/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    img_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    response = send_from_directory(img_dir, filename)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Private-Network'] = 'true'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response


# ── Places ──────────────────────────────────────────────────────────────
@app.route('/api/places', methods=['GET'])
def get_places():
    lang = request.args.get('lang', 'ar')
    category = request.args.get('category')

    query = Place.query
    if category:
        query = query.filter(Place.categories.like(f'%{category}%'))

    places = query.all()
    result = []
    for place in places:
        trans = PlaceTranslation.query.filter_by(place_id=place.id, lang=lang).first()
        trans_en = PlaceTranslation.query.filter_by(place_id=place.id, lang='en').first()

        result.append({
            'id': place.id,
            'photo': _resolve_photo(place.photo_url),
            'emoji': place.emoji,
            'cats': place.categories.split(',') if place.categories else [],
            'badge': {
                'ar': _get_badge(place.id, 'ar'),
                'fr': _get_badge(place.id, 'fr'),
                'en': _get_badge(place.id, 'en'),
            },
            'name': {
                'ar': _get_field(place.id, 'ar', 'name'),
                'fr': _get_field(place.id, 'fr', 'name'),
                'en': _get_field(place.id, 'en', 'name'),
            },
            'desc': {
                'ar': _get_field(place.id, 'ar', 'description'),
                'fr': _get_field(place.id, 'fr', 'description'),
                'en': _get_field(place.id, 'en', 'description'),
            },
            'history': {
                'ar': _get_field(place.id, 'ar', 'history'),
                'fr': _get_field(place.id, 'fr', 'history'),
                'en': _get_field(place.id, 'en', 'history'),
            },
            'rating': place.rating,
            'visit': {
                'ar': _get_field(place.id, 'ar', 'visit_duration'),
                'fr': _get_field(place.id, 'fr', 'visit_duration'),
                'en': _get_field(place.id, 'en', 'visit_duration'),
            },
            'map': place.map_url,
            'qr': place.qr_code,
            'source': place.image_source,
            'sourceUrl': place.image_source_url,
            'infoSource': place.info_source,
        })
    return jsonify(result)


@app.route('/api/places/<int:place_id>', methods=['GET'])
def get_place(place_id):
    place = Place.query.get_or_404(place_id)
    return jsonify({
        'id': place.id,
        'photo': _resolve_photo(place.photo_url),
        'emoji': place.emoji,
        'cats': place.categories.split(',') if place.categories else [],
        'badge': {
            'ar': _get_badge(place.id, 'ar'),
            'fr': _get_badge(place.id, 'fr'),
            'en': _get_badge(place.id, 'en'),
        },
        'name': {
            'ar': _get_field(place.id, 'ar', 'name'),
            'fr': _get_field(place.id, 'fr', 'name'),
            'en': _get_field(place.id, 'en', 'name'),
        },
        'desc': {
            'ar': _get_field(place.id, 'ar', 'description'),
            'fr': _get_field(place.id, 'fr', 'description'),
            'en': _get_field(place.id, 'en', 'description'),
        },
        'history': {
            'ar': _get_field(place.id, 'ar', 'history'),
            'fr': _get_field(place.id, 'fr', 'history'),
            'en': _get_field(place.id, 'en', 'history'),
        },
        'rating': place.rating,
        'visit': {
            'ar': _get_field(place.id, 'ar', 'visit_duration'),
            'fr': _get_field(place.id, 'fr', 'visit_duration'),
            'en': _get_field(place.id, 'en', 'visit_duration'),
        },
        'map': place.map_url,
        'qr': place.qr_code,
        'source': place.image_source,
        'sourceUrl': place.image_source_url,
        'infoSource': place.info_source,
        'references': _get_references(place.id),
    })


# ── QR Code resolution ───────────────────────────────────────────────────
@app.route('/api/qr/<string:code>', methods=['GET'])
def resolve_qr(code):
    qr = QRCode.query.filter_by(code=code).first()
    if not qr:
        return jsonify({'error': 'QR code not found'}), 404
    place = Place.query.get(qr.place_id)
    if not place:
        return jsonify({'error': 'Place not found'}), 404
    return jsonify({
        'placeId': place.id,
        'name': {
            'ar': _get_field(place.id, 'ar', 'name'),
            'fr': _get_field(place.id, 'fr', 'name'),
            'en': _get_field(place.id, 'en', 'name'),
        },
        'mapUrl': place.map_url,
    })


# ── Categories ───────────────────────────────────────────────────────────
@app.route('/api/categories', methods=['GET'])
def get_categories():
    cats = Category.query.all()
    return jsonify([{
        'key': c.key,
        'icon': c.icon,
        'ar': c.name_ar,
        'fr': c.name_fr,
        'en': c.name_en,
        'allowedCats': c.allowed_cats.split(',') if c.allowed_cats else [],
    } for c in cats])


# ── Tours ────────────────────────────────────────────────────────────────
@app.route('/api/tours', methods=['GET'])
def get_tours():
    tours = Tour.query.all()
    result = []
    for t in tours:
        result.append({
            'id': t.id,
            'icon': t.icon,
            'photo': t.photo_url,
            'name': {
                'ar': _get_tour_field(t.id, 'ar', 'name'),
                'fr': _get_tour_field(t.id, 'fr', 'name'),
                'en': _get_tour_field(t.id, 'en', 'name'),
            },
            'desc': {
                'ar': _get_tour_field(t.id, 'ar', 'description'),
                'fr': _get_tour_field(t.id, 'fr', 'description'),
                'en': _get_tour_field(t.id, 'en', 'description'),
            },
            'badge': {
                'ar': _get_tour_field(t.id, 'ar', 'badge'),
                'fr': _get_tour_field(t.id, 'fr', 'badge'),
                'en': _get_tour_field(t.id, 'en', 'badge'),
            },
            'isDemo': t.is_demo,
        })
    return jsonify(result)


# ── Helper functions ─────────────────────────────────────────────────────
def _get_field(place_id, lang, field):
    trans = PlaceTranslation.query.filter_by(place_id=place_id, lang=lang).first()
    if not trans:
        return ''
    return getattr(trans, field, '') or ''


def _get_badge(place_id, lang):
    trans = PlaceTranslation.query.filter_by(place_id=place_id, lang=lang).first()
    return trans.badge if trans else ''


def _get_tour_field(tour_id, lang, field):
    trans = TourTranslation.query.filter_by(tour_id=tour_id, lang=lang).first()
    if not trans:
        return ''
    return getattr(trans, field, '') or ''


def _get_references(place_id):
    refs = Reference.query.filter_by(place_id=place_id).all()
    return [{'title': r.title, 'url': r.url, 'type': r.ref_type} for r in refs]


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
