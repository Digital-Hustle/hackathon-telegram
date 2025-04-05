import aiosqlite
from datetime import datetime


async def insert_new_user(user_id):
    async with aiosqlite.connect('user.db') as conn:
        current_date = datetime.now().strftime('%d.%m.%Y')
        async with conn.execute('INSERT OR IGNORE INTO user (user_id, reg_time) VALUES (?, ?)', (user_id, current_date)) as cursor:
            await conn.commit()
            affected_rows = cursor.rowcount

    return affected_rows