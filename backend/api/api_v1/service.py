from sqlalchemy import select
from core.models import User, db_helper
from sqlalchemy.ext.asyncio import AsyncSession



async def forgot_password(email):
    query = await db.execute(select(User).where(User.email == email))
    user = query.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    await send_mail()
    return {"message": "Email sent" }