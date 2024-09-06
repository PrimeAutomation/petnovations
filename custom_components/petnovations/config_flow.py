import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from .const import CONF_HOST, CONF_API_KEY, CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)

class PetnovationsConfigFlow(config_entries.ConfigFlow):
    VERSION = 1

    def __init__(self):
        self._host = None
        self._api_key = None
        self._refresh_token = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._api_key = user_input[CONF_API_KEY]
            self._refresh_token = user_input[CONF_REFRESH_TOKEN]
            return self.async_create_entry(
                title="Petnovations",
                data={
                    CONF_HOST: self._host,
                    CONF_API_KEY: self._api_key,
                    CONF_REFRESH_TOKEN: self._refresh_token
                }
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_REFRESH_TOKEN): str,
            })
        )
