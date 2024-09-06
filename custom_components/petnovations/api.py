import requests
from typing import Optional

class PetnovationsAPI:
    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
        self.token = None
        self.token_expiry = None

    def _get_new_token(self) -> Optional[str]:
        url = "https://iot.petnovations.com/facade/v1/mobile-user/refreshToken"
        response = requests.post(url, json={"refreshToken": self.refresh_token})
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            # Handle token expiry logic if needed
            return self.token
        return None

    def _request_with_token(self, url: str, method: str = 'GET', data: Optional[dict] = None):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.request(method, url, headers=headers, json=data)
        if response.status_code == 401 and response.json().get("code") == "TOKEN_NOT_VALID":
            # Token expired, refresh token
            self._get_new_token()
            headers["Authorization"] = f"Bearer {self.token}"
            response = requests.request(method, url, headers=headers, json=data)
        return response.json()

    def get_devices(self):
        url = "https://iot.petnovations.com/device/device"
        return self._request_with_token(url)
