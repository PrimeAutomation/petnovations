from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .api import PetnovationsAPI
from .coordinator import PetnovationsCoordinator
from .const import DOMAIN
import logging

CONF_REFRESH_TOKEN = "refresh_token"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Petnovations integration from a config entry."""
    _LOGGER.debug("Setting up Petnovations entry")
    
    api = PetnovationsAPI(entry.data[CONF_REFRESH_TOKEN])
    coordinator = PetnovationsCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    _LOGGER.debug("Coordinator setup complete")
    
    # Store the coordinator with entry_id in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")

    return True
