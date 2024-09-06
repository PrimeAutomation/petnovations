from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_SCAN_INTERVAL
import logging
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

class PetnovationsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="Petnovations",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=15),
        )
        self.api = api

    async def _async_update_data(self):
        devices = self.api.get_devices()
        return devices

class PetnovationsSensor(Entity):
    def __init__(self, coordinator, device):
        self.coordinator = coordinator
        self.device = device

    @property
    def name(self):
        return self.device["name"]

    @property
    def state(self):
        return self.device["operationStatus"]["state"]

    async def async_update(self):
        await self.coordinator.async_request_refresh()
