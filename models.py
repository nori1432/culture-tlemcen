from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Place(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    photo_url = db.Column(db.Text, nullable=False)
    emoji = db.Column(db.String(10), nullable=False, default='📍')
    categories = db.Column(db.String(200))  # comma-separated: "historic,religious"
    rating = db.Column(db.String(20), default='★★★★☆')
    map_url = db.Column(db.Text, nullable=False)
    qr_code = db.Column(db.String(100))
    image_source = db.Column(db.String(200))
    image_source_url = db.Column(db.Text)
    info_source = db.Column(db.String(200))

    translations = db.relationship('PlaceTranslation', backref='place', lazy=True)
    references = db.relationship('Reference', backref='place', lazy=True)


class PlaceTranslation(db.Model):
    __tablename__ = 'place_translations'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)
    lang = db.Column(db.String(5), nullable=False)  # 'ar', 'fr', 'en'
    name = db.Column(db.String(200), nullable=False)
    badge = db.Column(db.String(100))
    description = db.Column(db.Text)
    history = db.Column(db.Text)
    visit_duration = db.Column(db.String(50))

    __table_args__ = (db.UniqueConstraint('place_id', 'lang'),)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(10))
    name_ar = db.Column(db.String(100))
    name_fr = db.Column(db.String(100))
    name_en = db.Column(db.String(100))
    allowed_cats = db.Column(db.String(200))  # comma-separated category filter


class QRCode(db.Model):
    __tablename__ = 'qr_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)


class Tour(db.Model):
    __tablename__ = 'tours'

    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(10))
    photo_url = db.Column(db.Text)
    is_demo = db.Column(db.Boolean, default=True)

    translations = db.relationship('TourTranslation', backref='tour', lazy=True)


class TourTranslation(db.Model):
    __tablename__ = 'tour_translations'

    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id'), nullable=False)
    lang = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(200))
    description = db.Column(db.Text)
    badge = db.Column(db.String(100))

    __table_args__ = (db.UniqueConstraint('tour_id', 'lang'),)


class Reference(db.Model):
    __tablename__ = 'references'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)
    title = db.Column(db.String(200))
    url = db.Column(db.Text)
    ref_type = db.Column(db.String(50))  # 'image', 'info', 'map'


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    icon = db.Column(db.String(10))
    name_ar = db.Column(db.String(100))
    name_fr = db.Column(db.String(100))
    name_en = db.Column(db.String(100))
    desc_ar = db.Column(db.Text)
    desc_fr = db.Column(db.Text)
    desc_en = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
