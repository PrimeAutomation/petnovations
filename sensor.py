import logging
import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_HOST, CONF_API_KEY, CONF_REFRESH_TOKEN, DEVICE_CLASS_TIMESTAMP
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_API_KEY): str,
    vol.Required(CONF_REFRESH_TOKEN): str,
})

async def async_setup_entry(hass, entry):
    coordinator = PetnovationsDataUpdateCoordinator(
        hass,
        entry.data[CONF_HOST],
        entry.data[CONF_API_KEY],
        entry.data[CONF_REFRESH_TOKEN],
    )
    await coordinator.async_refresh()

    hass.data.setdefault("petnovations", {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

class PetnovationsDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, api_key, refresh_token):
        super().__init__(
            hass,
            _LOGGER,
            name="petnovations",
            update_interval=timedelta(minutes=10),
        )
        self.host = host
        self.api_key = api_key
        self.refresh_token = refresh_token
        self.access_token = None
        self._refresh_access_token()

    def _refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        try:
            response = requests.post(
                f"{self.host}/facade/v1/mobile-user/refreshToken",
                json={"refreshToken": self.refresh_token},
            )
            response.raise_for_status()
            tokens = response.json()
            self.access_token = tokens.get("accessToken")
        except Exception as e:
            _LOGGER.error(f"Failed to refresh access token: {e}")
            self.access_token = None

    async def _async_update_data(self):
        """Fetch data from API with the current access token."""
        if not self.access_token:
            self._refresh_access_token()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            response = requests.get(
                f"{self.host}/device/device",
                headers=headers
            )
            if response.status_code == 401:  # Unauthorized, token may be expired
                self._refresh_access_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.get(
                    f"{self.host}/device/device",
                    headers=headers
                )
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            raise UpdateFailed(f"Error communicating with API: {e}")

class PetnovationsSensor(SensorEntity):
    def __init__(self, coordinator, device):
        self.coordinator = coordinator
        self.device = device
        self._attr_name = device["name"]
        self._attr_unique_id = device["manufacturerId"]
        self._attr_device_class = DEVICE_CLASS_TIMESTAMP
        self._attr_state = None

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()
        device_data = next(
            (device for device in self.coordinator.data["thingList"] if device["manufacturerId"] == self.device["manufacturerId"]),
            None
        )
        if device_data:
            self._attr_state = device_data["lastClean"]

    @property
    def extra_state_attributes(self):
        return {
            "totalSaniSolution": self.device.get("totalSaniSolution"),
            "remainingSaniSolution": self.device.get("remainingSaniSolution"),
        }
