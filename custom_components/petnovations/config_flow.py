import logging
import voluptuous as vol
from homeassistant import config_entries
from .const import CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)

class PetnovationsConfigFlow(config_entries.ConfigFlow):
    VERSION = 1

    def __init__(self):
        self._refresh_token = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._refresh_token = user_input[CONF_REFRESH_TOKEN]
            return self.async_create_entry(
                title="Petnovations",
                data={
                    CONF_REFRESH_TOKEN: self._refresh_token
                }
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_REFRESH_TOKEN): str,
            })
        )
