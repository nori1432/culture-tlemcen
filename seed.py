"""
Seed the MySQL database with initial Tlemcen Smart Tour data.
Run: python seed.py
"""

from app import app
from models import db, Place, PlaceTranslation, Category, QRCode, Tour, TourTranslation, Reference, Service

PLACES_DATA = [
    {
        'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Grande_Mosque_of_Tlemcen_1.jpg/640px-Grande_Mosque_of_Tlemcen_1.jpg',
        'emoji': '🕌', 'categories': 'religious,historic', 'rating': '★★★★★',
        'map': 'https://www.google.com/maps/search/Grande+Mosquée+Tlemcen/@34.8797,1.3168,17z',
        'qr': 'QR_GRANDE_MOSQUEE',
        'image_source': 'Wikimedia Commons – Public Domain',
        'image_source_url': 'https://commons.wikimedia.org/wiki/File:Grande_Mosque_of_Tlemcen_1.jpg',
        'info_source': 'Direction du Patrimoine Culturel de Tlemcen',
        'translations': {
            'ar': {'name': 'الجامع الكبير', 'badge': 'ديني', 'description': 'أحد أقدم المساجد في الجزائر، بُني في القرن 12 على يد المرابطين بتصميم أندلسي رائع.', 'history': 'شُيّد الجامع الكبير في عهد المرابطين في القرن الثاني عشر الميلادي، وتوسّع في العصر الزياني.', 'visit_duration': '30 دق'},
            'fr': {'name': 'Grande Mosquée', 'badge': 'Religieux', 'description': "L'une des plus anciennes mosquées d'Algérie, construite au XIIème s. par les Almoravides.", 'history': "La Grande Mosquée fut édifiée sous les Almoravides au XIIème siècle, puis agrandie à l'époque ziyanide.", 'visit_duration': '30 min'},
            'en': {'name': 'Grand Mosque', 'badge': 'Religious', 'description': 'One of the oldest mosques in Algeria, built in the 12th century by the Almoravids.', 'history': 'The Grand Mosque was built under the Almoravids in the 12th century and expanded during the Ziyanid era.', 'visit_duration': '30 min'},
        },
    },
    {
        'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Minaret_de_la_mosquee_de_Mansourah_%28Tlemcen%29.jpg/480px-Minaret_de_la_mosquee_de_Mansourah_%28Tlemcen%29.jpg',
        'emoji': '🏰', 'categories': 'historic,religious', 'rating': '★★★★★',
        'map': 'https://www.google.com/maps/search/Minaret+Mansourah+Tlemcen/@34.8879,1.2964,17z',
        'qr': 'QR_MANSOURAH',
        'image_source': 'Wikimedia Commons – CC BY-SA 3.0',
        'image_source_url': 'https://commons.wikimedia.org/wiki/File:Minaret_de_la_mosquee_de_Mansourah_(Tlemcen).jpg',
        'info_source': 'Ministère de la Culture – Algérie',
        'translations': {
            'ar': {'name': 'مسجد ومئذنة منصوره', 'badge': 'تاريخي', 'description': 'المئذنة الزيانية الشامخة شاهدة على عظمة الدولة الزيانية في القرن 14.', 'history': 'بُني مسجد منصوره في القرن الرابع عشر الميلادي في عهد السلطان أبو تاشفين الزياني.', 'visit_duration': '45 دق'},
            'fr': {'name': 'Mosquée et Minaret de Mansourah', 'badge': 'Historique', 'description': 'Le minaret ziyanide, symbole de la grandeur de la dynastie ziyanide au XIVème s.', 'history': "La mosquée de Mansourah fut construite au XIVème siècle sous le sultan Abu Tashfin ziyanide.", 'visit_duration': '45 min'},
            'en': {'name': 'Mansourah Mosque & Minaret', 'badge': 'Historic', 'description': 'The Ziyanid minaret, testament to the grandeur of the Ziyanid dynasty in the 14th century.', 'history': 'Mansourah Mosque was built in the 14th century under Sultan Abu Tashfin of the Ziyanid dynasty.', 'visit_duration': '45 min'},
        },
    },
    {
        'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Tlemcen_derb_sansla.jpg/480px-Tlemcen_derb_sansla.jpg',
        'emoji': '⭐', 'categories': 'historic', 'rating': '★★★★★',
        'map': 'https://www.google.com/maps/search/Derb+Sansla+Tlemcen/@34.8796,1.3145,17z',
        'qr': 'QR_DERB_SENSLA',
        'image_source': 'Wikimedia Commons – CC BY-SA',
        'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tlemcen_derb_sansla.jpg',
        'info_source': 'Office National du Tourisme Algérien',
        'translations': {
            'ar': {'name': 'درب السنسلة', 'badge': 'أندلسي', 'description': 'الحي الأندلسي العتيق في قلب تلمسان بأزقته الضيقة.', 'history': 'درب السنسلة حي أندلسي تاريخي يُعكس الحضارة الأندلسية في تلمسان.', 'visit_duration': '1 ساعة'},
            'fr': {'name': 'Derb Sensla', 'badge': 'Andalou', 'description': "Le quartier andalou historique au cœur de Tlemcen avec ses ruelles étroites.", 'history': 'Derb Sensla est un quartier andalou historique reflétant la civilisation andalouse.', 'visit_duration': '1 heure'},
            'en': {'name': 'Derb Sensla', 'badge': 'Andalusian', 'description': 'The ancient Andalusian quarter at the heart of Tlemcen with unique narrow alleyways.', 'history': 'Derb Sensla is a historic Andalusian quarter reflecting the Andalusian civilization in Tlemcen.', 'visit_duration': '1 hour'},
        },
    },
    {
        'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Tlemcen_vue_lalla_setti.jpg/640px-Tlemcen_vue_lalla_setti.jpg',
        'emoji': '🌿', 'categories': 'nature', 'rating': '★★★★★',
        'map': 'https://www.google.com/maps/search/Lalla+Setti+Tlemcen/@34.9040,1.3020,17z',
        'qr': 'QR_LALLA_SETTI',
        'image_source': 'Wikimedia Commons – CC BY-SA',
        'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tlemcen_vue_lalla_setti.jpg',
        'info_source': 'Parc National de Tlemcen',
        'translations': {
            'ar': {'name': 'منتزه لالة سيتي', 'badge': 'طبيعي', 'description': 'منتزه طبيعي تاريخي على تل مشرف على تلمسان.', 'history': 'يقع منتزه لالة سيتي على تلة مشرفة على مدينة تلمسان.', 'visit_duration': '2 ساعة'},
            'fr': {'name': 'Parc Lalla Setti', 'badge': 'Naturel', 'description': 'Parc naturel historique sur une colline dominant toute la ville de Tlemcen.', 'history': 'Le parc Lalla Setti est situé sur une colline surplombant la ville.', 'visit_duration': '2 heures'},
            'en': {'name': 'Lalla Setti Park', 'badge': 'Natural', 'description': 'A historic natural park on a hill overlooking the entire city of Tlemcen.', 'history': 'Lalla Setti Park sits on a hill overlooking the city.', 'visit_duration': '2 hours'},
        },
    },
    {
        'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Tlemcen_Sidi_Boumediene_mosque_and_mausoleum.jpg/640px-Tlemcen_Sidi_Boumediene_mosque_and_mausoleum.jpg',
        'emoji': '🏺', 'categories': 'religious,museum,historic', 'rating': '★★★★★',
        'map': 'https://www.google.com/maps/search/Sidi+Boumediene+Tlemcen/@34.8920,1.3060,17z',
        'qr': 'QR_SIDI_BOUMEDIENE',
        'image_source': 'Wikimedia Commons – CC BY-SA',
        'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tlemcen_Sidi_Boumediene_mosque_and_mausoleum.jpg',
        'info_source': 'Ministère de la Culture – Algérie',
        'translations': {
            'ar': {'name': 'ضريح سيدي بومدين', 'badge': 'روحي', 'description': 'مجمع ديني رائع يضم ضريح الولي الصالح أبو مدين شعيب.', 'history': 'سيدي بومدين (أبو مدين شعيب) توفي عام 1197م. المجمع شُيّد في عهد السلطان الزياني.', 'visit_duration': '1 ساعة'},
            'fr': {'name': 'Mausolée Sidi Boumediene', 'badge': 'Spirituel', 'description': 'Remarquable complexe religieux comprenant le mausolée de Sidi Boumediene.', 'history': 'Sidi Boumediene est décédé en 1197. Le complexe fut érigé sous le sultan ziyanide.', 'visit_duration': '1 heure'},
            'en': {'name': 'Sidi Boumediene Mausoleum', 'badge': 'Spiritual', 'description': 'A remarkable religious complex including the mausoleum of Sidi Boumediene.', 'history': 'Sidi Boumediene died in 1197. The complex was built under Ziyanid Sultan Abu Hammu Moussa I.', 'visit_duration': '1 hour'},
        },
    },
    {
        'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Tlemcen-mechouar.jpg/640px-Tlemcen-mechouar.jpg',
        'emoji': '🏛️', 'categories': 'historic', 'rating': '★★★★☆',
        'map': 'https://www.google.com/maps/search/El+Mechouar+Palace+Tlemcen/@34.8825,1.3140,17z',
        'qr': 'QR_MECHOUAR',
        'image_source': 'Wikimedia Commons – CC BY-SA',
        'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tlemcen-mechouar.jpg',
        'info_source': 'Direction du Patrimoine Culturel de Tlemcen',
        'translations': {
            'ar': {'name': 'قصر المشوار', 'badge': 'أثري', 'description': 'القلعة الملكية الزيانية التي كانت مقر السلطة والحكم.', 'history': 'قصر المشوار كان مقر حكم الدولة الزيانية من القرن 13 إلى القرن 15.', 'visit_duration': '1 ساعة'},
            'fr': {'name': 'Palais El Mechouar', 'badge': 'Archéologique', 'description': 'La forteresse royale ziyanide qui était le siège du pouvoir.', 'history': "Le Palais El Mechouar était le siège du pouvoir de la dynastie ziyanide du XIIIème au XVème siècle.", 'visit_duration': '1 heure'},
            'en': {'name': 'El Mechouar Palace', 'badge': 'Archaeological', 'description': 'The Ziyanid royal fortress that was the seat of power and governance.', 'history': 'El Mechouar Palace was the seat of Ziyanid dynasty rule from the 13th to 15th centuries.', 'visit_duration': '1 hour'},
        },
    },
    {
        'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Tlemcen_musee.jpg/480px-Tlemcen_musee.jpg',
        'emoji': '🎨', 'categories': 'museum', 'rating': '★★★★☆',
        'map': 'https://www.google.com/maps/search/Musée+de+Tlemcen/@34.8817,1.3156,17z',
        'qr': None,
        'image_source': 'Wikimedia Commons – CC BY-SA',
        'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tlemcen_musee.jpg',
        'info_source': 'Musée National de Tlemcen',
        'translations': {
            'ar': {'name': 'متحف الفن والتاريخ', 'badge': 'متحف', 'description': 'يحتضن مجموعة نفيسة من التحف الأثرية والفنون الأندلسية.', 'history': 'متحف تلمسان للفن والتاريخ يضم مجموعات أثرية تتناول حضارة تلمسان عبر العصور.', 'visit_duration': '1.5 ساعة'},
            'fr': {'name': "Musée des Arts et de l'Histoire", 'badge': 'Musée', 'description': "Abrite une précieuse collection d'artefacts archéologiques et d'arts andalous.", 'history': "Le musée de Tlemcen abrite des collections archéologiques couvrant la civilisation à travers les âges.", 'visit_duration': '1h30'},
            'en': {'name': 'Museum of Art and History', 'badge': 'Museum', 'description': 'Houses a precious collection of archaeological artifacts and Andalusian arts.', 'history': 'Tlemcen Museum of Art and History holds archaeological collections spanning Berber, Roman, Christian and Islamic periods.', 'visit_duration': '1.5 hours'},
        },
    },
    {
        'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Remparts_tlemcen.jpg/480px-Remparts_tlemcen.jpg',
        'emoji': '🏗️', 'categories': 'historic', 'rating': '★★★☆☆',
        'map': 'https://www.google.com/maps/search/Remparts+Tlemcen/@34.8820,1.3180,16z',
        'qr': None,
        'image_source': 'Wikimedia Commons – CC BY-SA',
        'image_source_url': 'https://commons.wikimedia.org/wiki/File:Remparts_tlemcen.jpg',
        'info_source': 'Direction du Patrimoine Culturel de Tlemcen',
        'translations': {
            'ar': {'name': 'سور تلمسان القديم', 'badge': 'تاريخي', 'description': 'بقايا أسوار مدينة تلمسان القديمة التي شيدها الزيانيون.', 'history': 'أسوار تلمسان القديمة بُنيت في عصر الدولة الزيانية.', 'visit_duration': '45 دق'},
            'fr': {'name': 'Remparts de Tlemcen', 'badge': 'Historique', 'description': 'Vestiges des remparts érigés par les Ziyanides pour protéger la capitale.', 'history': 'Les remparts de Tlemcen furent construits à l\'époque ziyanide.', 'visit_duration': '45 min'},
            'en': {'name': 'Old Walls of Tlemcen', 'badge': 'Historic', 'description': 'Remains of the old city walls built by the Ziyanids to protect the capital.', 'history': "Tlemcen's old walls were built during the Ziyanid period.", 'visit_duration': '45 min'},
        },
    },
]

CATEGORIES_DATA = [
    {'key': 'tourist', 'icon': '🎒', 'name_ar': 'سائح', 'name_fr': 'Touriste', 'name_en': 'Tourist', 'allowed_cats': 'historic,religious,nature,museum,leisure'},
    {'key': 'researcher', 'icon': '📚', 'name_ar': 'باحث', 'name_fr': 'Chercheur', 'name_en': 'Researcher', 'allowed_cats': 'historic,religious,museum'},
    {'key': 'business', 'icon': '🏢', 'name_ar': 'أعمال', 'name_fr': 'Affaires', 'name_en': 'Business', 'allowed_cats': 'leisure,nature'},
    {'key': 'family', 'icon': '👨‍👩‍👦', 'name_ar': 'عائلة', 'name_fr': 'Famille', 'name_en': 'Family', 'allowed_cats': 'nature,leisure,museum'},
    {'key': 'photographer', 'icon': '📸', 'name_ar': 'مصور', 'name_fr': 'Photographe', 'name_en': 'Photographer', 'allowed_cats': 'historic,nature,museum,religious'},
    {'key': 'student', 'icon': '🎓', 'name_ar': 'طالب', 'name_fr': 'Étudiant', 'name_en': 'Student', 'allowed_cats': 'historic,museum,religious'},
]

TOURS_DATA = [
    {'icon': '⭐', 'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Tlemcen_derb_sansla.jpg/480px-Tlemcen_derb_sansla.jpg', 'is_demo': True,
     'translations': {
         'ar': {'name': 'درب السنسلة', 'description': 'جولة 360° في الحي الأندلسي العتيق', 'badge': 'جولة 360°'},
         'fr': {'name': 'Derb Sensla', 'description': 'Visite 360° dans le quartier andalou', 'badge': 'Visite 360°'},
         'en': {'name': 'Derb Sensla', 'description': '360° tour of the ancient Andalusian quarter', 'badge': '360° Tour'},
     }},
    {'icon': '🏰', 'photo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Minaret_de_la_mosquee_de_Mansourah_%28Tlemcen%29.jpg/480px-Minaret_de_la_mosquee_de_Mansourah_%28Tlemcen%29.jpg', 'is_demo': True,
     'translations': {
         'ar': {'name': 'منصوره', 'description': 'استكشاف المئذنة الزيانية الشامخة', 'badge': 'جولة افتراضية'},
         'fr': {'name': 'Mansourah', 'description': 'Exploration du minaret ziyanide', 'badge': 'Visite virtuelle'},
         'en': {'name': 'Mansourah', 'description': 'Exploration of the Ziyanid minaret', 'badge': 'Virtual Tour'},
     }},
]

SERVICES_DATA = [
    {'key': 'restaurants', 'icon': '🍽️', 'name_ar': 'مطاعم', 'name_fr': 'Restaurants', 'name_en': 'Restaurants', 'desc_ar': 'مطاعم تقليدية وعصرية في تلمسان', 'desc_fr': 'Restaurants traditionnels et modernes', 'desc_en': 'Traditional and modern restaurants in Tlemcen'},
    {'key': 'hotels', 'icon': '🏨', 'name_ar': 'فنادق', 'name_fr': 'Hôtels', 'name_en': 'Hotels', 'desc_ar': 'فنادق ومرافق إقامة', 'desc_fr': 'Hôtels et hébergements', 'desc_en': 'Hotels and accommodation'},
    {'key': 'transport', 'icon': '🚌', 'name_ar': 'النقل', 'name_fr': 'Transport', 'name_en': 'Transport', 'desc_ar': 'معلومات النقل والمواصلات', 'desc_fr': 'Informations sur les transports', 'desc_en': 'Transport information'},
]


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed places
        place_map = {}
        for pd in PLACES_DATA:
            place = Place(
                photo_url=pd['photo'], emoji=pd['emoji'],
                categories=pd['categories'], rating=pd['rating'],
                map_url=pd['map'], qr_code=pd.get('qr'),
                image_source=pd['image_source'],
                image_source_url=pd['image_source_url'],
                info_source=pd['info_source'],
            )
            db.session.add(place)
            db.session.flush()
            place_map[pd['translations']['en']['name']] = place.id

            for lang, trans in pd['translations'].items():
                t = PlaceTranslation(
                    place_id=place.id, lang=lang,
                    name=trans['name'], badge=trans.get('badge'),
                    description=trans.get('description'),
                    history=trans.get('history'),
                    visit_duration=trans.get('visit_duration'),
                )
                db.session.add(t)

            if pd.get('qr'):
                qr = QRCode(code=pd['qr'], place_id=place.id)
                db.session.add(qr)

            # Add references
            ref_img = Reference(place_id=place.id, title='Wikimedia Commons', url=pd['image_source_url'], ref_type='image')
            ref_map = Reference(place_id=place.id, title='Google Maps', url=pd['map'], ref_type='map')
            ref_info = Reference(place_id=place.id, title=pd['info_source'], url='', ref_type='info')
            db.session.add_all([ref_img, ref_map, ref_info])

        # Seed categories
        for cd in CATEGORIES_DATA:
            cat = Category(**cd)
            db.session.add(cat)

        # Seed tours
        for td in TOURS_DATA:
            tour = Tour(icon=td['icon'], photo_url=td['photo'], is_demo=td['is_demo'])
            db.session.add(tour)
            db.session.flush()
            for lang, trans in td['translations'].items():
                tt = TourTranslation(tour_id=tour.id, lang=lang, **trans)
                db.session.add(tt)

        # Seed services
        for sd in SERVICES_DATA:
            svc = Service(**sd)
            db.session.add(svc)

        db.session.commit()
        print('✅ Database seeded successfully!')


if __name__ == '__main__':
    seed()
