from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_API_KEY

class PetnovationsConfigFlow(config_entries.ConfigFlow):
    VERSION = 1

    def __init__(self):
        self._host = None
        self._api_key = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._api_key = user_input[CONF_API_KEY]
            return self.async_create_entry(
                title="Petnovations",
                data={
                    CONF_HOST: self._host,
                    CONF_API_KEY: self._api_key
                }
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_API_KEY): str,
            })
        )
