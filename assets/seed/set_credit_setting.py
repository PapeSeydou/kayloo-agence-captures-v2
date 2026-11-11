
import os, sys
from pathlib import Path
ROOT = Path(r"C:/Users/log/OneDrive/Bureau/SEPRO/kayloo_siteweb")
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///" + (ROOT/".agents/capture-v2/capture.db").as_posix()
os.environ["TESTING"]="true"; os.environ["ENVIRONMENT"]="dev"; os.environ["EMAIL_ENABLED"]="false"
sys.path.insert(0, str(ROOT/"app")); os.chdir(ROOT/"app")
import asyncio
from sqlalchemy import select
from core.auth import get_async_session_context
from models.setting import Setting
async def main():
    async with get_async_session_context() as s:
        for key, val in (("free_credits_per_agency_kayloo", "1"),
                         ("free_credits_per_agency_immoneuf", "1"),
                         ("publication_credit_cost_property", "1")):
            st = (await s.execute(select(Setting).where(Setting.key == key))).scalar_one_or_none()
            if st is None:
                s.add(Setting(key=key, value=val)); print("added", key, val)
            else:
                st.value = val; print("set", key, "=", val)
        await s.commit()
asyncio.run(main())
