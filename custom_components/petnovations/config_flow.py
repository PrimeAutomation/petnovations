import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

class PetnovationsConfigFlow(config_entries.ConfigFlow):
    VERSION = 1

    def __init__(self):
        self._host = None
        self._api_key = None
        self._refresh_token = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._host = user_input["host"]
            self._api_key = user_input["api_key"]
            self._refresh_token = user_input["refresh_token"]
            return self.async_create_entry(
                title="Petnovations",
                data={
                    "host": self._host,
                    "api_key": self._api_key,
                    "refresh_token": self._refresh_token
                }
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Required("api_key"): str,
                vol.Required("refresh_token"): str,
            })
        )
