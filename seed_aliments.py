"""
Script d'injection de 100 aliments fitness en base de données.
Usage : python seed_aliments.py
À exécuter depuis la racine du projet (là où se trouve run.py).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import create_app
from backend.extensions import db
from backend.models import Aliment

app = create_app()

aliments = [
    # ── PROTÉINES ANIMALES ──────────────────────────────────────────
    {"name": "Poulet (blanc)",         "calories": 165, "proteines": 31.0, "glucides": 0.0,  "lipides": 3.6},
    {"name": "Dinde (blanc)",          "calories": 135, "proteines": 30.0, "glucides": 0.0,  "lipides": 1.0},
    {"name": "Boeuf haché 5%",         "calories": 137, "proteines": 21.0, "glucides": 0.0,  "lipides": 5.0},
    {"name": "Steak de boeuf",         "calories": 197, "proteines": 26.0, "glucides": 0.0,  "lipides": 10.0},
    {"name": "Saumon",                 "calories": 208, "proteines": 20.0, "glucides": 0.0,  "lipides": 13.0},
    {"name": "Thon en boite (eau)",    "calories": 116, "proteines": 26.0, "glucides": 0.0,  "lipides": 1.0},
    {"name": "Cabillaud",              "calories": 82,  "proteines": 18.0, "glucides": 0.0,  "lipides": 0.7},
    {"name": "Crevettes",              "calories": 99,  "proteines": 24.0, "glucides": 0.2,  "lipides": 0.3},
    {"name": "Oeuf entier",            "calories": 155, "proteines": 13.0, "glucides": 1.1,  "lipides": 11.0},
    {"name": "Blanc d'oeuf",           "calories": 52,  "proteines": 11.0, "glucides": 0.7,  "lipides": 0.2},
    {"name": "Sardines en boite",      "calories": 208, "proteines": 25.0, "glucides": 0.0,  "lipides": 11.0},
    {"name": "Maquereau",              "calories": 205, "proteines": 19.0, "glucides": 0.0,  "lipides": 14.0},
    {"name": "Porc filet",             "calories": 143, "proteines": 26.0, "glucides": 0.0,  "lipides": 4.0},
    {"name": "Jambon blanc",           "calories": 107, "proteines": 18.0, "glucides": 1.5,  "lipides": 3.5},
    {"name": "Tilapia",                "calories": 96,  "proteines": 20.0, "glucides": 0.0,  "lipides": 2.0},

    # ── PROTÉINES VÉGÉTALES ─────────────────────────────────────────
    {"name": "Tofu ferme",             "calories": 76,  "proteines": 8.0,  "glucides": 1.9,  "lipides": 4.8},
    {"name": "Tempeh",                 "calories": 193, "proteines": 19.0, "glucides": 9.4,  "lipides": 11.0},
    {"name": "Lentilles (cuites)",     "calories": 116, "proteines": 9.0,  "glucides": 20.0, "lipides": 0.4},
    {"name": "Pois chiches (cuits)",   "calories": 164, "proteines": 8.9,  "glucides": 27.0, "lipides": 2.6},
    {"name": "Haricots rouges",        "calories": 127, "proteines": 8.7,  "glucides": 22.8, "lipides": 0.5},
    {"name": "Haricots noirs",         "calories": 132, "proteines": 8.9,  "glucides": 23.7, "lipides": 0.5},
    {"name": "Edamame",                "calories": 122, "proteines": 11.0, "glucides": 9.9,  "lipides": 5.2},
    {"name": "Seitan",                 "calories": 370, "proteines": 75.0, "glucides": 14.0, "lipides": 1.9},
    {"name": "Protéine de soja",       "calories": 338, "proteines": 81.0, "glucides": 4.8,  "lipides": 3.4},

    # ── FÉCULENTS & CÉRÉALES ────────────────────────────────────────
    {"name": "Riz blanc (cuit)",       "calories": 130, "proteines": 2.7,  "glucides": 28.0, "lipides": 0.3},
    {"name": "Riz complet (cuit)",     "calories": 112, "proteines": 2.6,  "glucides": 24.0, "lipides": 0.9},
    {"name": "Flocons d'avoine",       "calories": 389, "proteines": 17.0, "glucides": 66.0, "lipides": 7.0},
    {"name": "Quinoa (cuit)",          "calories": 120, "proteines": 4.4,  "glucides": 21.3, "lipides": 1.9},
    {"name": "Patate douce",           "calories": 86,  "proteines": 1.6,  "glucides": 20.0, "lipides": 0.1},
    {"name": "Pomme de terre",         "calories": 77,  "proteines": 2.0,  "glucides": 17.0, "lipides": 0.1},
    {"name": "Pâtes complètes (cuites)","calories": 124, "proteines": 5.0,  "glucides": 25.0, "lipides": 1.1},
    {"name": "Pain complet",           "calories": 247, "proteines": 9.0,  "glucides": 41.0, "lipides": 3.4},
    {"name": "Boulgour (cuit)",        "calories": 83,  "proteines": 3.1,  "glucides": 18.6, "lipides": 0.2},
    {"name": "Millet (cuit)",          "calories": 119, "proteines": 3.5,  "glucides": 23.7, "lipides": 1.0},
    {"name": "Sarrasin (cuit)",        "calories": 92,  "proteines": 3.4,  "glucides": 19.9, "lipides": 0.6},
    {"name": "Maïs (cuit)",            "calories": 96,  "proteines": 3.4,  "glucides": 21.0, "lipides": 1.5},

    # ── LÉGUMES ─────────────────────────────────────────────────────
    {"name": "Brocoli",                "calories": 34,  "proteines": 2.8,  "glucides": 6.6,  "lipides": 0.4},
    {"name": "Épinards",               "calories": 23,  "proteines": 2.9,  "glucides": 3.6,  "lipides": 0.4},
    {"name": "Courgette",              "calories": 17,  "proteines": 1.2,  "glucides": 3.1,  "lipides": 0.3},
    {"name": "Poivron rouge",          "calories": 31,  "proteines": 1.0,  "glucides": 6.0,  "lipides": 0.3},
    {"name": "Poivron vert",           "calories": 20,  "proteines": 0.9,  "glucides": 4.6,  "lipides": 0.2},
    {"name": "Tomate",                 "calories": 18,  "proteines": 0.9,  "glucides": 3.9,  "lipides": 0.2},
    {"name": "Concombre",              "calories": 15,  "proteines": 0.7,  "glucides": 3.6,  "lipides": 0.1},
    {"name": "Chou-fleur",             "calories": 25,  "proteines": 1.9,  "glucides": 5.0,  "lipides": 0.3},
    {"name": "Chou kale",              "calories": 49,  "proteines": 4.3,  "glucides": 8.8,  "lipides": 0.9},
    {"name": "Asperges",               "calories": 20,  "proteines": 2.2,  "glucides": 3.9,  "lipides": 0.1},
    {"name": "Haricots verts",         "calories": 31,  "proteines": 1.8,  "glucides": 7.0,  "lipides": 0.1},
    {"name": "Champignons",            "calories": 22,  "proteines": 3.1,  "glucides": 3.3,  "lipides": 0.3},
    {"name": "Oignon",                 "calories": 40,  "proteines": 1.1,  "glucides": 9.3,  "lipides": 0.1},
    {"name": "Ail",                    "calories": 149, "proteines": 6.4,  "glucides": 33.0, "lipides": 0.5},
    {"name": "Carotte",                "calories": 41,  "proteines": 0.9,  "glucides": 9.6,  "lipides": 0.2},
    {"name": "Céleri",                 "calories": 16,  "proteines": 0.7,  "glucides": 3.0,  "lipides": 0.2},
    {"name": "Aubergine",              "calories": 25,  "proteines": 1.0,  "glucides": 5.9,  "lipides": 0.2},
    {"name": "Betterave",              "calories": 43,  "proteines": 1.6,  "glucides": 9.6,  "lipides": 0.2},
    {"name": "Artichaut",              "calories": 53,  "proteines": 2.9,  "glucides": 10.5, "lipides": 0.2},

    # ── FRUITS ──────────────────────────────────────────────────────
    {"name": "Banane",                 "calories": 89,  "proteines": 1.1,  "glucides": 23.0, "lipides": 0.3},
    {"name": "Pomme",                  "calories": 52,  "proteines": 0.3,  "glucides": 14.0, "lipides": 0.2},
    {"name": "Myrtilles",              "calories": 57,  "proteines": 0.7,  "glucides": 14.5, "lipides": 0.3},
    {"name": "Fraises",                "calories": 32,  "proteines": 0.7,  "glucides": 7.7,  "lipides": 0.3},
    {"name": "Orange",                 "calories": 47,  "proteines": 0.9,  "glucides": 12.0, "lipides": 0.1},
    {"name": "Mangue",                 "calories": 60,  "proteines": 0.8,  "glucides": 15.0, "lipides": 0.4},
    {"name": "Ananas",                 "calories": 50,  "proteines": 0.5,  "glucides": 13.0, "lipides": 0.1},
    {"name": "Kiwi",                   "calories": 61,  "proteines": 1.1,  "glucides": 15.0, "lipides": 0.5},
    {"name": "Avocat",                 "calories": 160, "proteines": 2.0,  "glucides": 9.0,  "lipides": 15.0},
    {"name": "Cerises",                "calories": 63,  "proteines": 1.1,  "glucides": 16.0, "lipides": 0.2},

    # ── PRODUITS LAITIERS & OEUFS ───────────────────────────────────
    {"name": "Fromage blanc 0%",       "calories": 45,  "proteines": 8.0,  "glucides": 3.8,  "lipides": 0.2},
    {"name": "Yaourt grec nature",     "calories": 97,  "proteines": 9.0,  "glucides": 3.6,  "lipides": 5.0},
    {"name": "Skyr nature",            "calories": 57,  "proteines": 11.0, "glucides": 3.5,  "lipides": 0.2},
    {"name": "Lait demi-écrémé",       "calories": 46,  "proteines": 3.3,  "glucides": 4.8,  "lipides": 1.6},
    {"name": "Mozzarella",             "calories": 280, "proteines": 28.0, "glucides": 2.2,  "lipides": 17.0},
    {"name": "Parmesan",               "calories": 431, "proteines": 38.0, "glucides": 4.1,  "lipides": 29.0},
    {"name": "Cottage cheese",         "calories": 98,  "proteines": 11.0, "glucides": 3.4,  "lipides": 4.3},

    # ── GRAISSES & OLÉAGINEUX ───────────────────────────────────────
    {"name": "Huile d'olive",          "calories": 884, "proteines": 0.0,  "glucides": 0.0,  "lipides": 100.0},
    {"name": "Huile de coco",          "calories": 862, "proteines": 0.0,  "glucides": 0.0,  "lipides": 100.0},
    {"name": "Beurre de cacahuète",    "calories": 588, "proteines": 25.0, "glucides": 20.0, "lipides": 50.0},
    {"name": "Amandes",                "calories": 579, "proteines": 21.0, "glucides": 22.0, "lipides": 50.0},
    {"name": "Noix",                   "calories": 654, "proteines": 15.0, "glucides": 14.0, "lipides": 65.0},
    {"name": "Noix de cajou",          "calories": 553, "proteines": 18.0, "glucides": 30.0, "lipides": 44.0},
    {"name": "Graines de chia",        "calories": 486, "proteines": 17.0, "glucides": 42.0, "lipides": 31.0},
    {"name": "Graines de lin",         "calories": 534, "proteines": 18.0, "glucides": 29.0, "lipides": 42.0},
    {"name": "Graines de courge",      "calories": 559, "proteines": 30.0, "glucides": 11.0, "lipides": 49.0},
    {"name": "Tahini",                 "calories": 595, "proteines": 17.0, "glucides": 21.0, "lipides": 54.0},

    # ── DIVERS / CONDIMENTS FITNESS ─────────────────────────────────
    {"name": "Protéine whey",          "calories": 380, "proteines": 80.0, "glucides": 8.0,  "lipides": 5.0},
    {"name": "Miel",                   "calories": 304, "proteines": 0.3,  "glucides": 82.0, "lipides": 0.0},
    {"name": "Sauce soja",             "calories": 53,  "proteines": 8.1,  "glucides": 4.9,  "lipides": 0.1},
    {"name": "Levure nutritionnelle",  "calories": 325, "proteines": 50.0, "glucides": 29.0, "lipides": 5.0},
    {"name": "Lait de coco",           "calories": 230, "proteines": 2.3,  "glucides": 5.5,  "lipides": 24.0},
    {"name": "Lait d'amande",          "calories": 13,  "proteines": 0.4,  "glucides": 0.3,  "lipides": 1.1},
    {"name": "Vinaigre balsamique",    "calories": 88,  "proteines": 0.5,  "glucides": 17.0, "lipides": 0.0},
    {"name": "Concentré de tomate",    "calories": 82,  "proteines": 4.3,  "glucides": 18.0, "lipides": 0.5},
    {"name": "Bouillon de poulet",     "calories": 15,  "proteines": 2.5,  "glucides": 1.4,  "lipides": 0.5},
    {"name": "Farine d'avoine",        "calories": 375, "proteines": 13.0, "glucides": 66.0, "lipides": 7.0},
    {"name": "Farine de riz",          "calories": 366, "proteines": 6.0,  "glucides": 80.0, "lipides": 1.4},
    {"name": "Cacao en poudre",        "calories": 228, "proteines": 20.0, "glucides": 58.0, "lipides": 14.0},
    {"name": "Sirop d'érable",         "calories": 260, "proteines": 0.0,  "glucides": 67.0, "lipides": 0.1},
]

def seed():
    with app.app_context():
        count = 0
        for item in aliments:
            existing = Aliment.query.filter_by(name=item["name"]).first()
            if not existing:
                a = Aliment(
                    name=item["name"],
                    calories=item["calories"],
                    proteines=item["proteines"],
                    glucides=item["glucides"],
                    lipides=item["lipides"]
                )
                db.session.add(a)
                count += 1
        db.session.commit()
        print(f"✅ {count} aliments ajoutés en base ({len(aliments) - count} déjà existants).")

if __name__ == "__main__":
    seed()
