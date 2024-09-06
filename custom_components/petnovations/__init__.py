from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from .api import PetnovationsAPI
from .sensor import PetnovationsCoordinator

# Define your own constant for refresh token
CONF_REFRESH_TOKEN = "refresh_token"

async def async_setup_entry(hass, config_entry):
    refresh_token = config_entry.data[CONF_REFRESH_TOKEN]
    api = PetnovationsAPI(refresh_token)
    coordinator = PetnovationsCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault("petnovations", {})
    hass.data["petnovations"]["coordinator"] = coordinator

    # Add devices and sensors
    for device in coordinator.data["thingList"]:
        hass.helpers.discovery.async_load_platform(
            "sensor",
            "petnovations",
            {**config_entry.data, "device": device},
            config_entry,
        )
    return True

