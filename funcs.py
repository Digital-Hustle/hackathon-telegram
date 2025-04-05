import aiosqlite
from datetime import datetime
import aiohttp

from typing import Optional, Dict, Any
from config import BASE_URL


async def insert_new_user(user_id):
    async with aiosqlite.connect('user.db') as conn:
        current_date = datetime.now().strftime('%d.%m.%Y')
        async with conn.execute('INSERT OR IGNORE INTO user (user_id, reg_time) VALUES (?, ?)', (user_id, current_date)) as cursor:
            await conn.commit()
            affected_rows = cursor.rowcount

    return affected_rows


async def check_login(user_id: int) -> bool:
    async with aiosqlite.connect('user.db') as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                'SELECT username FROM user WHERE user_id = ? AND username IS NOT NULL AND username != ""',
                (user_id,)
            )
            result = await cursor.fetchone()
            return result is not None



async def jwt_insert(user_id, access_token=None, refresh_token=None):
    async with aiosqlite.connect('user.db') as conn:
        if access_token is not None:
            async with conn.execute('''
                INSERT INTO user (user_id, access_token) 
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET access_token = ?
            ''', (user_id, access_token, access_token)) as cursor:
                await conn.commit()

        if refresh_token is not None:
            async with conn.execute('''
                INSERT INTO user (user_id, refresh_token) 
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET refresh_token = ?
            ''', (user_id, refresh_token, refresh_token)) as cursor:
                await conn.commit()



async def register_user(username: str, password: str, confirm_password: str) -> bool:
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": username,
        "password": password,
        "passwordConfirmation": confirm_password
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            return response.status == 200


async def auth_user(user_id, username: str, password: str) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": username,
        "password": password
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status == 200:
                response_data = await response.json()

                username = response_data.get("username")
                access_token = response_data.get("accessToken")
                refresh_token = response_data.get("refreshToken")

                await jwt_insert(user_id, access_token=access_token, refresh_token=refresh_token)
                await username_insert(user_id, username)

                return True
            return False


async def username_insert(user_id: int, username: str) -> None:
    async with aiosqlite.connect('user.db') as conn:
        await conn.execute('''
            INSERT INTO user (user_id, username) 
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username = ?
        ''', (user_id, username, username))
        await conn.commit()


async def user_logout(user_id: int) -> None:
    async with aiosqlite.connect('user.db') as conn:
        await conn.execute('''
            UPDATE user 
            SET access_token = NULL, 
                refresh_token = NULL,
                username = NULL
            WHERE user_id = ?
        ''', (user_id,))
        await conn.commit()


async def get_user_tokens(user_id: int) -> Optional[Dict[str, str]]:
    async with aiosqlite.connect('user.db') as conn:
        async with conn.execute('''
            SELECT access_token, refresh_token FROM user WHERE user_id = ?
        ''', (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                return {
                    'access_token': result[0],
                    'refresh_token': result[1]
                }
            return None

async def refresh_token(user_id: int) -> bool:
    tokens = await get_user_tokens(user_id)
    if not tokens or not tokens.get('refresh_token'):
        return False

    url = f"{BASE_URL}/auth/refresh"
    payload = {
        "refreshToken": tokens['refresh_token']
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    await jwt_insert(
                        user_id=user_id,
                        access_token=data['accessToken'],
                        refresh_token=data['refreshToken']
                    )
                    return True
                else:
                    return False

    except Exception as e:
        print(f"Ошибка при обновлении токена: {str(e)}")
        return False