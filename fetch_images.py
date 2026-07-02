"""
Fetch one real Wikimedia Commons image URL per place.
Writes results to images_result.json  — then incorporated into seed_places.py.
Run: python fetch_images.py
Requires: pip install requests
"""

import json
import time
import requests

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "TlemcenSmartTour/1.0 (educational tourism app)"})

COMMONS = "https://commons.wikimedia.org/w/api.php"
WIKI_FR = "https://fr.wikipedia.org/w/api.php"
WIKI_EN = "https://en.wikipedia.org/w/api.php"
WIKI_AR = "https://ar.wikipedia.org/w/api.php"

# ── Hardcoded verified images for the most famous places ─────────────────────
OVERRIDE = {
    22: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Grande_Mosqu%C3%A9e_de_Tlemcen.jpg/640px-Grande_Mosqu%C3%A9e_de_Tlemcen.jpg",
    38: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Mansourah_Mosque_04.jpg/640px-Mansourah_Mosque_04.jpg",
    41: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Porte_de_la_mosqu%C3%A9e_de_Sidi_Boum%C3%A9di%C3%A8ne%2C_Tlemcen.jpg/640px-Porte_de_la_mosqu%C3%A9e_de_Sidi_Boum%C3%A9di%C3%A8ne%2C_Tlemcen.jpg",
    74: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Porte_de_la_mosqu%C3%A9e_de_Sidi_Boum%C3%A9di%C3%A8ne%2C_Tlemcen.jpg/640px-Porte_de_la_mosqu%C3%A9e_de_Sidi_Boum%C3%A9di%C3%A8ne%2C_Tlemcen.jpg",
    88: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Palais_machouar.jpg/640px-Palais_machouar.jpg",
    89: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Palais_machouar.jpg/640px-Palais_machouar.jpg",
    91: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Palais_machouar.jpg/640px-Palais_machouar.jpg",
    167: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Palais_machouar.jpg/640px-Palais_machouar.jpg",
     2: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Lala_Setti_%D9%84%D8%A7%D9%84%D8%A9_%D8%B3%D8%AA%D9%8A_-_panoramio.jpg/640px-Lala_Setti_%D9%84%D8%A7%D9%84%D8%A9_%D8%B3%D8%AA%D9%8A_-_panoramio.jpg",
     5: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Mansourah_Mosque_04.jpg/640px-Mansourah_Mosque_04.jpg",
    78: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Lala_Setti_%D9%84%D8%A7%D9%84%D8%A9_%D8%B3%D8%AA%D9%8A_-_panoramio.jpg/640px-Lala_Setti_%D9%84%D8%A7%D9%84%D8%A9_%D8%B3%D8%AA%D9%8A_-_panoramio.jpg",
    151: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Mansourah_Mosque_04.jpg/640px-Mansourah_Mosque_04.jpg",
    159: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Mansourah_Mosque_04.jpg/640px-Mansourah_Mosque_04.jpg",
    160: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Mansourah_Mosque_04.jpg/640px-Mansourah_Mosque_04.jpg",
}

# Place data: (num, french_name, english_search)
PLACES_META = [
    (1,  "Tlemcen ville", "Tlemcen Algeria city"),
    (2,  "Plateau de Lalla Setti Tlemcen", "Lalla Setti Tlemcen"),
    (3,  "Quartier Agadir Tlemcen", "Agadir Tlemcen archaeological"),
    (4,  "Tagrart Tlemcen medina", "Tagrart Tlemcen"),
    (5,  "Mansourah Tlemcen", "Mansourah mosque Tlemcen"),
    (6,  "El Eubbad Tlemcen", "Eubbad Tlemcen"),
    (7,  "Mosquée Sidi El Haloui Tlemcen", "Sidi El Haloui mosque Tlemcen"),
    (8,  "Boudghene Tlemcen", "Boudghene Tlemcen"),
    (9,  "Chetouane Tlemcen", "Chetouane Algeria"),
    (10, "Sidi Said Tlemcen", "Sidi Said mosque Tlemcen"),
    (11, "Oued Safsaf Tlemcen", "Tlemcen Algeria"),
    (12, "Oued Meshkana Tlemcen", "Agadir Tlemcen"),
    (13, "Minaret Agadir Tlemcen", "Agadir minaret Tlemcen"),
    (14, "Mosquée Sidi El Haloui Tlemcen", "Sidi El Haloui mosque Tlemcen"),
    (15, "Mosquée Sidi Eldjebbar Tlemcen", "Sidi Djebbar mosque Tlemcen"),
    (16, "Mosquée Sidi El Yeddoun Tlemcen", "mosque Tlemcen medina"),
    (17, "Mosquée Sidi Bellahsen Tlemcen", "Sidi Bellahsen mosque Tlemcen"),
    (18, "Mosquée Bab Zir Tlemcen", "mosque Tlemcen"),
    (19, "Mosquée des Chorfas Tlemcen", "mosque Tlemcen medina"),
    (20, "Mosquée Lalla Gheriba Tlemcen", "mosque Tlemcen"),
    (21, "Grande Mosquée Tlemcen", "Grand mosque Tlemcen"),
    (22, "Grande Mosquée de Tlemcen", "Grand mosque Tlemcen"),
    (23, "Mosquée Sidi Snouci Tlemcen", "mosque Tlemcen medina"),
    (24, "mosquée Tlemcen", "mosque Tlemcen"),
    (25, "Mosquée Sidi Abu al-Hasan Tlemcen", "Sidi Bellahsen mosque Tlemcen"),
    (26, "Mosquée Lalla Reya Tlemcen", "mosque Tlemcen"),
    (27, "Mosquée Sidi El Kalai Tlemcen", "mosque Tlemcen"),
    (28, "Ibn Marzouq mosquée Tlemcen", "mosque Tlemcen"),
    (29, "mosquée Tlemcen médina", "mosque Tlemcen medina"),
    (30, "mosquée Tlemcen", "mosque Tlemcen"),
    (31, "Mosquée Ouled el-Imam Tlemcen", "mosque Tlemcen"),
    (32, "Mosquée Sidi Brahim El Masmoudi Tlemcen", "mosque Tlemcen"),
    (33, "mosquée Tlemcen médina", "mosque Tlemcen"),
    (34, "mosquée Tlemcen", "mosque Tlemcen"),
    (35, "Mosquée Sidi Ouazzen Tlemcen", "mosque Tlemcen"),
    (36, "Mosquée El Mechouar Tlemcen", "El Mechouar mosque Tlemcen"),
    (37, "mosquée Tlemcen médina", "mosque Tlemcen"),
    (38, "Minaret de Mansourah Tlemcen", "Mansourah minaret Tlemcen"),
    (39, "oratoire Boudghene Tlemcen", "mosque Tlemcen"),
    (40, "Minaret Sidi Ishaq Tlemcen", "minaret Tlemcen"),
    (41, "Mosquée Sidi Boumediene Tlemcen", "Sidi Boumediene mosque Tlemcen"),
    (42, "Mausolée Sidi Daoudi Tlemcen", "mausoleum Tlemcen"),
    (43, "Mausolée Sidi Wahab Tlemcen", "mausoleum Tlemcen"),
    (44, "Mausolée Sidi Yaqub Tlemcen", "mausoleum Tlemcen"),
    (45, "coupole Tlemcen", "dome Tlemcen"),
    (46, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (47, "Mausolée Sidi El Haloui Tlemcen", "Sidi El Haloui Tlemcen"),
    (48, "sanctuaire Sidi El Haloui Tlemcen", "Sidi El Haloui Tlemcen"),
    (49, "Mausolée Sidi Bellahsen Tlemcen", "Sidi Bellahsen Tlemcen"),
    (50, "cimetière Tlemcen", "Tlemcen historical cemetery"),
    (51, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (52, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (53, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (54, "Moulay Yacoub Tlemcen", "mausoleum Tlemcen"),
    (55, "Mausolée Sidi Bellahsen Tlemcen", "Sidi Bellahsen Tlemcen"),
    (56, "Mausolée Ibn Marzouq Tlemcen", "Ibn Marzouq mausoleum"),
    (57, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (58, "sanctuaire Tlemcen", "mausoleum Tlemcen"),
    (59, "Mausolée Sidi Brahim Tlemcen", "mausoleum Tlemcen"),
    (60, "Mausolée Sidi Boumediene Tlemcen", "mausoleum Tlemcen"),
    (61, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (62, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (63, "coupole Tlemcen", "dome Tlemcen"),
    (64, "Mausolée El Eubbad Tlemcen", "mausoleum Tlemcen"),
    (65, "Mausolée Sidi Ishaq Tlemcen", "mausoleum Tlemcen"),
    (66, "cimetière Sidi Sinoussi Tlemcen", "cemetery Tlemcen"),
    (67, "Mausolée Sidi Sinoussi Tlemcen", "mausoleum Tlemcen"),
    (68, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (69, "cimetière chrétien Tlemcen", "cemetery Tlemcen"),
    (70, "coupoles Tlemcen", "dome Tlemcen"),
    (71, "Medersa Khaldounia Tlemcen", "mausoleum Tlemcen"),
    (72, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (73, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (74, "Mausolée Sidi Boumediene Tlemcen", "Sidi Boumediene mausoleum Tlemcen"),
    (75, "Mausolée Sidi Abdelkader Tlemcen", "mausoleum Tlemcen"),
    (76, "Mausolée Sidi Abdellah Lbaal Tlemcen", "mausoleum Tlemcen"),
    (77, "Mausolée Tlemcen", "mausoleum Tlemcen"),
    (78, "Mausolée Lalla Setti Tlemcen", "Lalla Setti Tlemcen"),
    (79, "Khalwa Sidi Senoussi Tlemcen", "zawiya Tlemcen"),
    (80, "Medersa Tlemcen", "medersa Tlemcen"),
    (81, "Medersa Ouled el Imam Tlemcen", "medersa Tlemcen"),
    (82, "Medersa Abu al-Hasan Tlemcen", "medersa Tlemcen"),
    (83, "demeure médina Tlemcen", "traditional house Tlemcen"),
    (84, "demeure médina Tlemcen", "traditional house Tlemcen"),
    (85, "demeure médina Tlemcen", "traditional house Tlemcen"),
    (86, "maison Mohammed Dib Tlemcen", "Mohammed Dib Tlemcen"),
    (87, "demeure médina Tlemcen", "traditional house Tlemcen"),
    (88, "Palais El Mechouar Tlemcen", "El Mechouar Palace Tlemcen"),
    (89, "Palais El Mechouar Tlemcen", "El Mechouar Palace Tlemcen"),
    (90, "maison pèlerins Tlemcen médina", "Tlemcen medina"),
    (91, "Palais du Sultan Tlemcen", "Sultan Palace Tlemcen"),
    (92, "demeure médina Tlemcen", "traditional house Tlemcen"),
    (93, "fondouk Tlemcen médina", "fondouk caravanserai Tlemcen"),
    (94, "fondouk Tlemcen", "caravanserai Tlemcen"),
    (95, "fondouk Tlemcen", "caravanserai Tlemcen"),
    (96, "fondouk Tlemcen", "caravanserai Tlemcen"),
    (97, "fondouk Tlemcen", "caravanserai Tlemcen"),
    (98, "fondouk Tlemcen", "caravanserai Tlemcen"),
    (99, "fondouk Tlemcen", "caravanserai Tlemcen"),
    (100,"fondouk Tlemcen", "caravanserai Tlemcen"),
    (101,"fondouk Tlemcen", "caravanserai Tlemcen"),
    (102,"hammam médina Tlemcen", "hammam bath Tlemcen"),
    (103,"hammam Agadir Tlemcen", "hammam bath Tlemcen"),
    (104,"hammam médina Tlemcen", "hammam bath Tlemcen"),
    (105,"hammam Tlemcen", "hammam bath Tlemcen"),
    (106,"hammam Tlemcen", "hammam bath Tlemcen"),
    (107,"hammam Tlemcen", "hammam bath Tlemcen"),
    (108,"hammam Tlemcen", "hammam bath Tlemcen"),
    (109,"hammam Tlemcen", "hammam bath Tlemcen"),
    (110,"hammam Tlemcen", "hammam bath Tlemcen"),
    (111,"hammam Tlemcen", "hammam Tlemcen"),
    (112,"hammam Tlemcen", "hammam bath Tlemcen"),
    (113,"hammam Tlemcen", "hammam bath Tlemcen"),
    (114,"hammam El Eubbad Tlemcen", "hammam Eubbad Tlemcen"),
    (115,"fontaine médina Tlemcen", "fountain Tlemcen medina"),
    (116,"Mosquée Sidi El Haloui Tlemcen fontaine", "Sidi El Haloui Tlemcen"),
    (117,"puits médina Tlemcen", "well Tlemcen medina"),
    (118,"citerne Tlemcen", "cistern Tlemcen"),
    (119,"grande citerne Tlemcen", "cistern Tlemcen"),
    (120,"fontaine Tlemcen", "fountain Tlemcen"),
    (121,"fontaine Sidi Boumediene Tlemcen", "Sidi Boumediene Tlemcen"),
    (122,"puits Sidi Boumediene Tlemcen", "Sidi Boumediene Tlemcen"),
    (123,"qissaria Tlemcen souk", "souk market Tlemcen"),
    (124,"derb médina Tlemcen", "alley Tlemcen medina"),
    (125,"derb médina Tlemcen", "alley Tlemcen medina"),
    (126,"derb médina Tlemcen", "alley Tlemcen medina"),
    (127,"derb Tlemcen", "alley Tlemcen medina"),
    (128,"derb Tlemcen", "alley Tlemcen medina"),
    (129,"derb Tlemcen", "alley Tlemcen medina"),
    (130,"derb Tlemcen", "alley Tlemcen medina"),
    (131,"derb Tlemcen", "alley Tlemcen medina"),
    (132,"derb Tlemcen", "alley Tlemcen"),
    (133,"derb Tlemcen", "alley Tlemcen"),
    (134,"derb Tlemcen médina", "alley Tlemcen medina"),
    (135,"derb Tlemcen", "alley Tlemcen"),
    (136,"derb Tlemcen", "alley Tlemcen"),
    (137,"derb Tlemcen", "alley Tlemcen"),
    (138,"derb sept arches Tlemcen", "alley Tlemcen medina"),
    (139,"four médina Tlemcen", "traditional oven Tlemcen"),
    (140,"four Agadir Tlemcen", "Tlemcen historical"),
    (141,"four Tlemcen", "traditional oven Tlemcen"),
    (142,"four médina Tlemcen", "traditional oven Tlemcen"),
    (143,"four médina Tlemcen", "traditional oven Tlemcen"),
    (144,"Bab El Hadid Tlemcen", "gate Tlemcen"),
    (145,"four médina Tlemcen", "traditional oven Tlemcen"),
    (146,"remparts Agadir Tlemcen", "ramparts Tlemcen"),
    (147,"remparts Tagrart Tlemcen", "ramparts Tlemcen"),
    (148,"remparts Tagrart Tlemcen", "walls Tlemcen"),
    (149,"remparts Tlemcen", "walls Tlemcen"),
    (150,"remparts Tlemcen", "walls Tlemcen"),
    (151,"remparts Mansourah Tlemcen", "Mansourah walls Tlemcen"),
    (152,"tours Agadir Tlemcen", "tower Tlemcen"),
    (153,"tour Bab Hammam Tlemcen", "tower Tlemcen"),
    (154,"tour Tlemcen oued", "tower Tlemcen"),
    (155,"tour Agadir Tlemcen", "tower Tlemcen"),
    (156,"tours Tagrart Tlemcen", "tower Tlemcen"),
    (157,"tour Bab El Hadid Tlemcen", "tower Tlemcen"),
    (158,"tour Tlemcen médina", "tower Tlemcen"),
    (159,"tours Mansourah Tlemcen", "Mansourah Tlemcen"),
    (160,"fossés Mansourah Tlemcen", "Mansourah Tlemcen"),
    (161,"Bab El Kermadine Tlemcen", "Bab Kermadine gate Tlemcen"),
    (162,"Bab El Khemis Tlemcen", "Bab Khemis gate Tlemcen"),
    (163,"Bab Zir Tlemcen", "gate Tlemcen"),
    (164,"Bab El Rouah Tlemcen", "gate Tlemcen"),
    (165,"Bab El Hadid Tlemcen", "Bab Hadid Tlemcen"),
    (166,"Bab Touita Tlemcen", "gate Tlemcen"),
    (167,"Château El Mechouar Tlemcen", "El Mechouar castle Tlemcen"),
    (168,"château Tlemcen médina", "castle Tlemcen"),
]

# ── High-quality fallback images per topic ────────────────────────────────────
# These are verified Wikimedia Commons images of Tlemcen
FALLBACKS = {
    "mosque":     "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Grande_Mosqu%C3%A9e_de_Tlemcen.jpg/640px-Grande_Mosqu%C3%A9e_de_Tlemcen.jpg",
    "mausoleum":  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Porte_de_la_mosqu%C3%A9e_de_Sidi_Boum%C3%A9di%C3%A8ne%2C_Tlemcen.jpg/640px-Porte_de_la_mosqu%C3%A9e_de_Sidi_Boum%C3%A9di%C3%A8ne%2C_Tlemcen.jpg",
    "palace":     "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Palais_machouar.jpg/640px-Palais_machouar.jpg",
    "military":   "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Tlemcen_1836.jpg/640px-Tlemcen_1836.jpg",
    "mansourah":  "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Mansourah_Mosque_04.jpg/640px-Mansourah_Mosque_04.jpg",
    "lalla_setti":"https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Lala_Setti_%D9%84%D8%A7%D9%84%D8%A9_%D8%B3%D8%AA%D9%8A_-_panoramio.jpg/640px-Lala_Setti_%D9%84%D8%A7%D9%84%D8%A9_%D8%B3%D8%AA%D9%8A_-_panoramio.jpg",
    "medina":     "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Tlemcen_derb_sansla.jpg/480px-Tlemcen_derb_sansla.jpg",
    "geo":        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Lala_Setti_%D9%84%D8%A7%D9%84%D8%A9_%D8%B3%D8%AA%D9%8A_-_panoramio.jpg/640px-Lala_Setti_%D9%84%D8%A7%D9%84%D8%A9_%D8%B3%D8%AA%D9%8A_-_panoramio.jpg",
    "default":    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Grande_Mosqu%C3%A9e_de_Tlemcen.jpg/640px-Grande_Mosqu%C3%A9e_de_Tlemcen.jpg",
}

# Topic hints per place num → which fallback to use
TOPIC = {
    **{n: "mosque"    for n in range(13, 42)},
    **{n: "mausoleum" for n in range(42, 79)},
    **{n: "mosque"    for n in range(79, 83)},
    **{n: "palace"    for n in range(83, 102)},
    **{n: "medina"    for n in range(102, 146)},
    **{n: "military"  for n in range(146, 169)},
    **{n: "geo"       for n in range(1, 13)},
    2:  "lalla_setti",
    5:  "mansourah",
    38: "mansourah",
    78: "lalla_setti",
    88: "palace",
    89: "palace",
    91: "palace",
    151:"mansourah",
    159:"mansourah",
    160:"mansourah",
    161:"military",
    162:"military",
    167:"palace",
}


def get_commons_image(query: str) -> str | None:
    """Search Wikimedia Commons for an image; return thumbnail URL or None."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"File:{query}",
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 640,
        "format": "json",
        "gsrlimit": 5,
    }
    try:
        r = SESSION.get(COMMONS, params=params, timeout=12)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            url = info.get("thumburl") or info.get("url", "")
            if url and url.lower().endswith((".jpg", ".jpeg", ".png")):
                # Make sure it's a reasonable image (not too small filename)
                if "640px" in url or "thumb" in url:
                    return url
                # Accept direct url too
                return url
    except Exception:
        pass
    return None


def get_wikipedia_image(title: str, lang: str = "fr") -> str | None:
    """Get the main image from a Wikipedia article."""
    api = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "pageimages",
        "pithumbsize": 640,
        "format": "json",
    }
    try:
        r = SESSION.get(api, params=params, timeout=12)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            if page.get("ns") == 0 and "missing" not in page:
                src = page.get("thumbnail", {}).get("source", "")
                if src:
                    return src
    except Exception:
        pass
    return None


def get_commons_search(query: str) -> str | None:
    """Full-text search on Commons."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 640,
        "format": "json",
        "gsrlimit": 3,
    }
    try:
        r = SESSION.get(COMMONS, params=params, timeout=12)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            url = info.get("thumburl") or info.get("url", "")
            if url and any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png")):
                return url
    except Exception:
        pass
    return None


def fetch_image_for_place(num: int, fr_query: str, en_query: str) -> str:
    """Try multiple strategies to find an image, fall back to category default."""
    # Strategy 1: Try French Wikipedia
    url = get_wikipedia_image(fr_query, "fr")
    if url:
        print(f"  [{num:3d}] Wikipedia FR: {url[:80]}")
        return url

    # Strategy 2: Try English Wikipedia
    url = get_wikipedia_image(en_query, "en")
    if url:
        print(f"  [{num:3d}] Wikipedia EN: {url[:80]}")
        return url

    # Strategy 3: Try Commons file search
    url = get_commons_search(fr_query)
    if url:
        print(f"  [{num:3d}] Commons: {url[:80]}")
        return url

    # Strategy 4: Try Commons with English query
    url = get_commons_search(en_query)
    if url:
        print(f"  [{num:3d}] Commons EN: {url[:80]}")
        return url

    # Fallback: category image
    fb = FALLBACKS.get(TOPIC.get(num, "default"), FALLBACKS["default"])
    print(f"  [{num:3d}] Fallback({TOPIC.get(num, 'default')}): {fb[:80]}")
    return fb


def main():
    result = {}

    # Apply hardcoded overrides first
    for num, url in OVERRIDE.items():
        result[num] = url

    print(f"Fetching images for {len(PLACES_META)} places ...\n")
    for num, fr_query, en_query in PLACES_META:
        if num in OVERRIDE:
            print(f"  [{num:3d}] Override (hardcoded)")
            continue
        url = fetch_image_for_place(num, fr_query, en_query)
        result[num] = url
        time.sleep(0.4)  # polite rate limiting

    # Write JSON output
    with open("images_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Results saved to images_result.json ({len(result)} entries)")
    return result


if __name__ == "__main__":
    main()
