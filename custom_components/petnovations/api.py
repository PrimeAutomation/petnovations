import aiohttp
from typing import Optional
import asyncio

class PetnovationsAPI:
    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
        self.token = None

    async def _get_new_token(self) -> Optional[str]:
        url = "https://iot.petnovations.com/facade/v1/mobile-user/refreshToken"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"refreshToken": self.refresh_token}) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("token")
                    return self.token
        return None

    async def _request_with_token(self, url: str, method: str = 'GET', data: Optional[dict] = None):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                if response.status == 401 and (await response.json()).get("code") == "TOKEN_NOT_VALID":
                    # Token expired, refresh token
                    await self._get_new_token()
                    headers["Authorization"] = f"Bearer {self.token}"
                    async with session.request(method, url, headers=headers, json=data) as retry_response:
                        return await retry_response.json()
                return await response.json()

    async def get_devices(self):
        url = "https://iot.petnovations.com/device/device"
        return await self._request_with_token(url)
