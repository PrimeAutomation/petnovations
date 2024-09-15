import aiohttp
import logging
from typing import Optional

_LOGGER = logging.getLogger(__name__)

class PetnovationsAPI:
    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
        self.token = None

    async def _get_new_token(self):
        url = "https://iot.petnovations.com/facade/v1/mobile-user/refreshToken"
        json_payload = {"refreshToken": self.refresh_token}
        headers = {"Content-Type": "application/json"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload, headers=headers) as response:
                    response_json = await response.json()
                    _LOGGER.debug("Token response: %s", response_json)
                    if response_json.get("code") == "TOKEN_NOT_VALID":
                        _LOGGER.error("Token is not valid. Please provide a new refresh token.")
                        return None
                    self.token = response_json.get("token")
                    return self.token
        except Exception as e:
            _LOGGER.error("Error getting new token: %s", e)
            raise

    async def _request_with_token(self, url: str, method: str = 'GET', data: Optional[dict] = None):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                if response.status == 401:
                    data = await response.json()
                    if data.get("code") == "TOKEN_NOT_VALID":
                        _LOGGER.error("Token expired or invalid: %s", data.get("message"))
                        # Refresh token and retry the request
                        await self._get_new_token()
                        headers["Authorization"] = f"Bearer {self.token}"
                        async with session.request(method, url, headers=headers, json=data) as retry_response:
                            return await retry_

    async def get_devices(self):
        url = "https://iot.petnovations.com/device/device"
        if self.token is None:
            await self._get_new_token()
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_text = await response.text()
                    _LOGGER.debug("Device response text: %s", response_text)
                    response_json = await response.json()
                    
                    if response.status == 401:  # Unauthorized, token might be invalid
                        await self._get_new_token()
                        headers = {"Authorization": f"Bearer {self.token}"}
                        async with session.get(url, headers=headers) as retry_response:
                            retry_response_text = await retry_response.text()
                            _LOGGER.debug("Retry device response text: %s", retry_response_text)
                            return await retry_response.json()
                    
                    return response_json
        except Exception as e:
            _LOGGER.error("Error fetching devices: %s", e)
            raise                   
