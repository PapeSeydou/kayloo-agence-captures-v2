
"""Compte de test : agence + utilisateur + documents, etats 'pending' / 'validated' / 'reset'."""
import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app"
DB_PATH = ROOT / ".agents" / "capture-v2" / "capture.db"

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

import models  # noqa: F401
from sqlalchemy import event, select
from core.auth import User, create_user, get_async_session_context
from core.constants import UserRole
from core.db import engine
from models.agency import Agency
from models.agency_verification import AgencyVerification
from models.agent import Agent
from models.property import Property
from models.publication import Publication

AGENCY_NAME = "Agence Horizon Immobilier"
AGENCY_EMAIL = "contact@horizon-immo.com"
AGENCY_PHONE = "+221 77 123 45 67"
CONTACT_FIRST = "Awa"
CONTACT_LAST = "Diop"
ADMIN_EMAIL = "admin-capture@kayloo.immo"
PASSWORD = os.environ.get("CAPTURE_PASSWORD", "CaptureTest2026!")

DOCS = [
    ("NINEA.pdf", "ninea", "Agence Horizon Immobilier"),
    ("RCCM.pdf", "rc", "Agence Horizon Immobilier"),
    ("CNI.pdf", "cni", "Awa Diop"),
]

event.listen(engine.sync_engine, "connect", lambda conn, rec: conn.execute("PRAGMA journal_mode=WAL"))
event.listen(engine.sync_engine, "connect", lambda conn, rec: conn.execute("PRAGMA busy_timeout=15000"))


async def ensure_users():
    """Cree les deux comptes, un par un (chaque create_user ouvre sa session)."""
    async with get_async_session_context() as s:
        admin = (await s.execute(select(User).where(User.email == ADMIN_EMAIL))).scalar_one_or_none()
        manager = (await s.execute(select(User).where(User.email == AGENCY_EMAIL))).scalar_one_or_none()
    if admin is None:
        await create_user(email=ADMIN_EMAIL, password=PASSWORD, first_name="Admin", last_name="Kayloo",
                          phone_number="", gender="", role=UserRole.SUPERADMIN)
    if manager is None:
        await create_user(email=AGENCY_EMAIL, password=PASSWORD, first_name=CONTACT_FIRST, last_name=CONTACT_LAST,
                          phone_number="+221 78 456 78 90", gender="", role=UserRole.MANAGER)
    async with get_async_session_context() as s:
        admin = (await s.execute(select(User).where(User.email == ADMIN_EMAIL))).scalar_one()
        manager = (await s.execute(select(User).where(User.email == AGENCY_EMAIL))).scalar_one()
        admin.is_superuser = True; admin.is_active = True; admin.is_verified = True; admin.role = UserRole.SUPERADMIN
        manager.is_active = True; manager.is_verified = True; manager.role = UserRole.MANAGER
        await s.commit()
        return manager.id, admin.id


async def setup(state: str) -> None:
    manager_id, admin_id = await ensure_users()
    async with get_async_session_context() as s:
        manager = await s.get(User, manager_id)
        agency = (await s.execute(select(Agency).where(Agency.email == AGENCY_EMAIL))).scalar_one_or_none()
        if agency is None:
            agency = Agency(country="SN", name=AGENCY_NAME, email=AGENCY_EMAIL,
                            phone_number=AGENCY_PHONE, siteweb_url="www.horizon-immo.com",
                            max_agents=1, max_photos_per_property=10, is_active=False, is_verified=False)
            s.add(agency)
            await s.flush()
        agent = (await s.execute(select(Agent).where(Agent.user_id == manager.id, Agent.agency_id == agency.id))).scalar_one_or_none()
        if agent is None:
            s.add(Agent(user_id=manager.id, agency_id=agency.id))
            await s.flush()

        verifs = (await s.execute(select(AgencyVerification).where(AgencyVerification.agency_id == agency.id))).scalars().all()
        if state == "pending":
            agency.is_active = False
            agency.is_verified = False
            agency.verified_at = None
            for old in verifs:
                await s.delete(old)
            await s.flush()
            for filename, dtype, legal in DOCS:
                s.add(AgencyVerification(agency_id=agency.id, user_id=manager.id, legal_name=legal,
                                         document_type=dtype,
                                         document_url="/static/uploads/seed_docs/" + filename,
                                         status="pending"))
        else:
            agency.is_active = True
            agency.is_verified = True
            agency.verified_at = datetime.now(timezone.utc)
            for v in verifs:
                v.status = "approved"
                v.reviewed_at = datetime.now(timezone.utc)
                v.reviewed_by = ADMIN_EMAIL
            if state in ("reset", "validated"):
                agency.kayloo_plan_id = None
                agency.kayloo_plan_expires_at = None
                agency.kayloo_credits_granted_month = None
                agency.credit_balance_kayloo = 0
                agency.free_publications_used_kayloo = 0
                agency.max_active_listings_override_kayloo = None
            if state == "reset":
                props = (await s.execute(select(Property).where(Property.agency_id == agency.id))).scalars().all()
                for p in props:
                    for pub in (await s.execute(select(Publication).where(Publication.property_id == p.id))).scalars().all():
                        await s.delete(pub)
                    await s.flush()
                    await s.delete(p)
        await s.commit()
        print(f"etat={state} agency={agency.id} active={agency.is_active} verified={agency.is_verified} plan={agency.kayloo_plan_id}")


if __name__ == "__main__":
    state = sys.argv[1] if len(sys.argv) > 1 else "reset"
    asyncio.run(setup(state))
