from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .api import PetnovationsAPI
from .coordinator import PetnovationsCoordinator
from .sensor import PetnovationsSensor
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
    hass.data[DOMAIN] = {
        "coordinator": coordinator,
    }

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Create sensors
    hass.async_create_task(async_add_sensors(hass, coordinator))

    # Return True to indicate successful setup
    return True

async def async_add_sensors(hass: HomeAssistant, coordinator: PetnovationsCoordinator):
    """Create sensor entities for each device and key."""
    _LOGGER.debug("Adding sensors")
    devices = coordinator.data.get("thingList", [])
    sensors = []
    existing_sensor_ids = set()  # Track unique sensor IDs

    for device in devices:
        manufacturerId = device.get("manufacturerId", "unknown")

        # Add standard sensors
        standard_keys = [
            "lastClean", "remainingSaniSolution"
        ]
        for key in standard_keys:
            unique_id = f"{manufacturerId}_{key}"
            if unique_id not in existing_sensor_ids:
                _LOGGER.debug("Creating standard sensor with unique ID: %s", unique_id)
                sensors.append(PetnovationsSensor(coordinator, device, key))
                existing_sensor_ids.add(unique_id)
            else:
                _LOGGER.debug("Standard sensor with unique ID %s already exists", unique_id)

        # Add sensors for 'configuration' (nested object)
        if "configuration" in device:
            configuration_keys = ["volumeLevel"]
            for sub_key in configuration_keys:
                add_or_update_sensor(sub_key, device.get(sub_key))

    _LOGGER.debug("Created %d sensors", len(sensors))
    if sensors:
        # Use async_add_entities to add the created sensors
        async_add_entities(sensors)
