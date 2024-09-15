import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class PetnovationsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Petnovations data."""

    def __init__(self, hass, api):
        """Initialize the Petnovations coordinator."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name="Petnovations",
            update_interval=timedelta(seconds=5),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            data = await self.api.get_devices()
            if "thingList" in data:
                return data
            raise UpdateFailed("No 'thingList' found in response")
        except Exception as e:
            _LOGGER.error("Error fetching data: %s", e)
            raise UpdateFailed("Failed to fetch data from API")
