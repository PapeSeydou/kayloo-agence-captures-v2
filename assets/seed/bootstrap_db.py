
"""Bootstrap local de capture : SQLite + donnees alignees sur la slide 12 du deck V3.1.

Usage : python bootstrap_db.py [--reset]
"""
import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app"
DB_DIR = ROOT / ".agents" / "capture-v2"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "capture.db"

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///" + DB_PATH.as_posix()
for k in ("S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_BUCKET", "S3_ENDPOINT", "S3_REGION"):
    os.environ.pop(k, None)
os.environ["EMAIL_ENABLED"] = "false"
os.environ["ENVIRONMENT"] = "dev"
os.environ["TESTING"] = "true"
os.environ["ENABLE_STARTUP_SEED"] = "false"
os.environ["UPLOAD_DIR"] = str(APP / "static" / "uploads")
os.environ["APP_URL"] = "http://kayloo.local:8000"
os.environ["KAYLOO_DOMAIN"] = "kayloo.local:8000"

sys.path.insert(0, str(APP))
os.chdir(APP)

import importlib
import pkgutil

import models  # noqa: F401  (enregistre les tables exportees)

# Certains modeles ne sont pas reexportes par models/__init__ (ex. hero_banner) :
# on importe chaque module du paquet pour que create_all cree toutes les tables.
for _info in pkgutil.iter_modules(models.__path__):
    if not _info.name.startswith("_"):
        importlib.import_module("models." + _info.name)
from sqlalchemy import select
from core.auth import Base, User, create_user, get_async_session_context
from core.constants import UserRole
from models.agency import Agency
from models.agency_verification import AgencyVerification
from models.agent import Agent
from models.area import Area
from models.city import City
from models.country import Country
from models.property_rent_type import PropertyRentType
from models.property_type import PropertyType
from models.setting import Setting
from models.subscription_plan import SubscriptionPlan

AGENCY_NAME = "Agence Horizon Immobilier"
AGENCY_EMAIL = "contact@horizon-immo.com"
AGENCY_PHONE = "+221 77 123 45 67"
CONTACT_FIRST = "Awa"
CONTACT_LAST = "Diop"
ACCOUNT_EMAIL = AGENCY_EMAIL
ADMIN_EMAIL = "admin-capture@kayloo.local"
PASSWORD = os.environ.get("CAPTURE_PASSWORD", "CaptureTest2026!")

# Slide 12 — KAYLOO IMMO, ordre et valeurs du deck V3.1
KAYLOO_PLANS = [
    dict(code="decouverte", name="Découverte", price=0,       sort_order=0,
         max_active_listings=5,  max_agents=1, monthly_visibility_credits=5,
         featured_listings_per_month=0, has_featured_listings=False,
         max_qualified_leads_per_month=0, max_generic_leads_per_month=0),
    dict(code="standard",   name="Standard",   price=59000,   sort_order=1,
         max_active_listings=10, max_agents=1, monthly_visibility_credits=10,
         featured_listings_per_month=2, has_featured_listings=True,
         max_qualified_leads_per_month=2, max_generic_leads_per_month=None),
    dict(code="premium",    name="Premium",    price=88500,   sort_order=2,
         max_active_listings=30, max_agents=2, monthly_visibility_credits=30,
         featured_listings_per_month=5, has_featured_listings=True,
         max_qualified_leads_per_month=5, max_generic_leads_per_month=None),
    dict(code="business",   name="Business",   price=118000,  sort_order=3,
         max_active_listings=50, max_agents=3, monthly_visibility_credits=50,
         featured_listings_per_month=10, has_featured_listings=True,
         max_qualified_leads_per_month=None, max_generic_leads_per_month=None),
]

COUNTRIES = [
    ("SN", "Sénégal"), ("CI", "Côte d'Ivoire"), ("ML", "Mali"), ("GN", "Guinée"),
    ("TG", "Togo"), ("BJ", "Bénin"),
]
CITIES = [("dakar", "Dakar", "SN"), ("saly", "Saly", "SN"), ("thies", "Thiès", "SN")]
AREAS = [("dakar", "Almadies"), ("dakar", "Plateau"), ("dakar", "Mermoz"), ("saly", "Saly Portudal")]
PROPERTY_TYPES = [
    ("F2", "Studio"), ("F3", "Appartement F3"), ("F4", "Appartement F4"),
    ("F5", "Appartement F5"), ("DUPLEX", "Duplex"), ("VILLA", "Villa"),
    ("OFFICE", "Bureau"), ("MAGASIN", "Magasin"), ("LAND", "Terrain"), ("PARKING", "Parking"),
]
RENT_TYPES = [
    ("RENT_EMPTY", "Location Vide"), ("RENT_FURNISHED", "Location Meublée"), ("SALE", "Vente"),
]
SETTINGS = {
    "publication_credit_cost_property": ("1", "Coût en crédits — publication d'une annonce"),
    "publication_credit_cost_programme": ("1", "Coût en crédits — publication d'un programme"),
    "free_credits_per_agency_kayloo": ("0", "Publications gratuites par agence — Kayloo (0 = système désactivé)"),
    "free_credits_per_agency_immoneuf": ("0", "Publications gratuites par agence — ImmoNeuf (0 = système désactivé)"),
    "publication_duration_months": ("3", "Durée d'une publication (mois)"),
}


async def main(reset: bool) -> None:
    if reset and DB_PATH.exists():
        DB_PATH.unlink()
    from core.db import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("schema ok ->", DB_PATH)

    async with get_async_session_context() as s:
        # pays / villes / quartiers
        for code, name in COUNTRIES:
            if not (await s.execute(select(Country).where(Country.code == code))).scalar_one_or_none():
                s.add(Country(code=code, name=name, is_active=True))
        await s.flush()
        for code, name, cc in CITIES:
            if not (await s.execute(select(City).where(City.code == code))).scalar_one_or_none():
                s.add(City(code=code, name=name, country=cc, is_active=True))
        await s.flush()
        for city_code, aname in AREAS:
            exists = (await s.execute(select(Area).where(Area.city == city_code, Area.name == aname))).scalar_one_or_none()
            if not exists:
                s.add(Area(city=city_code, name=aname, is_active=True))
        for code, label in PROPERTY_TYPES:
            if not (await s.execute(select(PropertyType).where(PropertyType.code == code))).scalar_one_or_none():
                s.add(PropertyType(code=code, label=label, is_active=True))
        for code, label in RENT_TYPES:
            if not (await s.execute(select(PropertyRentType).where(PropertyRentType.code == code))).scalar_one_or_none():
                s.add(PropertyRentType(code=code, label=label, is_active=True))
        for key, (value, desc) in SETTINGS.items():
            if not (await s.execute(select(Setting).where(Setting.key == key))).scalar_one_or_none():
                s.add(Setting(key=key, value=value, description=desc))
        await s.commit()

        # equipements du bien (etape 3 du formulaire)
        from models.immo_commodity import ImmoCommodity
        COMMODITIES = [
            ("climatisation", "Climatisation", 1),
            ("parking", "Parking", 2),
            ("securite-24h", "Sécurité 24h/24", 3),
            ("balcon", "Balcon", 4),
            ("piscine", "Piscine", 5),
            ("jardin", "Jardin", 6),
            ("ascenseur", "Ascenseur", 7),
            ("meuble", "Meublé", 8),
        ]
        for slug, name, order in COMMODITIES:
            if not (await s.execute(select(ImmoCommodity).where(ImmoCommodity.slug == slug))).scalar_one_or_none():
                s.add(ImmoCommodity(name=name, slug=slug, display_order=order, icon_svg=""))
        await s.commit()
        print("commodities ok")

        # forfaits Kayloo = slide 12
        for spec in KAYLOO_PLANS:
            plan = (await s.execute(
                select(SubscriptionPlan).where(
                    SubscriptionPlan.portal == "kayloo", SubscriptionPlan.code == spec["code"])
            )).scalar_one_or_none()
            if plan is None:
                plan = SubscriptionPlan(portal="kayloo", code=spec["code"])
                s.add(plan)
            plan.name = spec["name"]
            plan.price = spec["price"]
            plan.billing_period = "trimestriel"
            plan.max_active_listings = spec["max_active_listings"]
            plan.max_agents = spec["max_agents"]
            plan.max_units = None
            plan.monthly_visibility_credits = spec["monthly_visibility_credits"]
            plan.featured_listings_per_month = spec["featured_listings_per_month"]
            plan.has_featured_listings = spec["has_featured_listings"]
            plan.max_qualified_leads_per_month = spec["max_qualified_leads_per_month"]
            plan.max_generic_leads_per_month = spec["max_generic_leads_per_month"]
            plan.is_custom = False
            plan.is_active = True
            plan.sort_order = spec["sort_order"]
        await s.commit()
        print("plans kayloo:", [p.name for p in (await s.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.portal == "kayloo").order_by(SubscriptionPlan.sort_order))).scalars()])
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main(reset="--reset" in sys.argv))
