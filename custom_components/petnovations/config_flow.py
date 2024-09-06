from homeassistant import config_entries
import voluptuous as vol
from homeassistant.const import CONF_SCAN_INTERVAL

# Define your own constant for refresh token
CONF_REFRESH_TOKEN = "refresh_token"

from .api import PetnovationsAPI

class PetnovationsConfigFlow(config_entries.ConfigFlow, domain="petnovations"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            refresh_token = user_input[CONF_REFRESH_TOKEN]
            api = PetnovationsAPI(refresh_token)
            token = await api._get_new_token()
            if token:
                return self.async_create_entry(
                    title="Petnovations",
                    data={CONF_REFRESH_TOKEN: refresh_token},
                )
            else:
                return self.async_abort(reason="Invalid refresh token")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_REFRESH_TOKEN): str,
            })
        )
