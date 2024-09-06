from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_API_KEY, CONF_REFRESH_TOKEN
from .const import DOMAIN


DOMAIN = "petnovations"

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    # Setup code here
    return True

async def async_unload_entry(hass, entry):
    # Unloading code here
    return True
