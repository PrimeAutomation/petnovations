from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.core import HomeAssistant, callback
from datetime import timedelta, datetime
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

class PetnovationsSensor(CoordinatorEntity):
    """Representation of a Petnovations sensor."""

    def __init__(self, coordinator, device, key, sub_key=None):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.device = device
        self.key = key
        self.sub_key = sub_key  # Support for nested keys
        
        # Determine if this is a nested key
        if sub_key:
            unique_key = f"{device.get('manufacturerId', 'unknown')}_{key}_{sub_key}"
            self._attr_name = self._format_name(f"{key}_{sub_key}")
        else:
            unique_key = f"{device.get('manufacturerId', 'unknown')}_{key}"
            self._attr_name = self._format_name(key)
        
        self._attr_unique_id = unique_key
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.get("manufacturerId", "unknown"))},
            "name": device.get("name", "Unknown"),
            "manufacturer": "Petnovations",
            "model": "CatGenie A.I.",
            "sw_version": device.get("fwVersion", "Unknown"),
            "hw_version": device.get("hwRevision", "Unknown"),
            "serial_number": device.get("manufacturerId", "Unknown"),
            "via_device": device.get("macAddress", "Unknown"),
            "connections": {("mac", device.get("macAddress", "Unknown"))}
        }

        diagnostic_class = ["error", ]
        sensors_class = ["Lastclean", "remainingSaniSolution"]
        configuration_class = []
        controls_class = []

        if key in diagnostic_class:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        elif key in configuration_class:
            self._attr_entity_category = EntityCategory.CONFIG
        elif key in controls_class:
            self._attr_entity_category = EntityCategory.CONFIG
        else:
            self._attr_entity_category = None

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return "Unknown"

        # Find the specific device from the coordinator data
        device = next((d for d in data.get("thingList", []) if d.get("manufacturerId") == self.device.get("manufacturerId")), None)
        if not device:
            return "Unknown"

        # Handle nested sensors for 'operationStatus' and 'configuration'
        if self.key in ["state", "progress", "error", "mode"]:
            value = device.get("operationStatus", {}).get(self.key)
        elif self.key in ["childLock", "volumeLevel", "mode", "manual"]:
            value = device.get("configuration", {}).get(self.key)
        else:
            value = device.get(self.key)

        # Handle None values
        if value is None:
            return "Unknown"

        # Handle date/time strings and format them
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value)
                value = self._format_datetime(value)
            except ValueError:
                pass  # Not a date string

        return value


    def _format_datetime(self, datetime_str):
        """Format ISO 8601 date/time string to a more readable format."""
        try:
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))  # Handle UTC format
            return dt.strftime("%m/%d/%Y - %I:%M%p")
        except ValueError:
            _LOGGER.warning("Invalid datetime format: %s", datetime_str)
            return datetime_str

    def _format_name(self, key):
        """Format the sensor name based on the key"""
        name = f"{self.device.get('name', 'Unknown')} {key}"
        return name.replace('_', ' ').title()

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Petnovations sensors from the platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    await coordinator.async_refresh()

    devices = coordinator.data.get("thingList", [])
    sensors = []

    for device in devices:
        # Add top-level sensors
        top_level_keys = ["lastClean", "remainingSaniSolution"]
        for key in top_level_keys:
            sensors.append(PetnovationsSensor(coordinator, device, key))

        # Add sensors for 'operationStatus' (nested object)
        if "operationStatus" in device:
            operation_keys = ["state", "progress", "error"]
            for sub_key in operation_keys:
                sensors.append(PetnovationsSensor(coordinator, device, "operationStatus", sub_key))

        # Add sensors for 'configuration' (nested object)
        if "configuration" in device:
            configuration_keys = ["volumeLevel"]
            for sub_key in configuration_keys:
                sensors.append(PetnovationsSensor(coordinator, device, "configuration", sub_key))

    async_add_entities(sensors)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Petnovations sensors from a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    await coordinator.async_refresh()

    async_setup_platform(hass, {}, async_add_entities)

    @callback
    def update_sensors():
        """Update the sensors."""
        _LOGGER.debug("Updating sensors...")
        new_entities = []
        existing_sensors = {entity.unique_id: entity for entity in hass.data[DOMAIN].get("sensors", [])}

        def add_or_update_sensor(entity_id, value):

            # Conditional logic for the 'progress' entity
            # if "progress" in entity_id:
            #     if value == 100:
            #         value = "Complete"
            #     elif value >= 75:
            #         value = "Almost Done"
            #     elif value >= 50:
            #         value = "Halfway There"
            #     elif value >= 25:
            #         value = "In Progress"
            #     else:
            #         value = "Just Started"

                # Conditional logic for the 'progress' entity
            if "state" in entity_id:
                if value == 0:
                    value = "Idle"
                elif value == 1:
                    value = "In Progress"
                elif value == 2:
                    value = "Paused"
                elif value == 3:
                    value = "Error"
                else:
                    value = "Checking..."

            """Helper function to add or update sensors."""
            if entity_id in existing_sensors:
                # Update the existing sensor's attributes
                sensor = existing_sensors[entity_id]
                sensor.device = device
                sensor._attr_state = value  # Set the updated value to the state attribute
                sensor.async_write_ha_state()  # Notify Home Assistant of the state change
            else:
                # Create a new sensor if it doesn't exist
                new_sensor = PetnovationsSensor(coordinator, device, entity_id)
                new_sensor._attr_state = value  # Set the initial state value
                new_entities.append(new_sensor)

        for device in coordinator.data.get("thingList", []):
            # Update direct sensors
            direct_keys = [
                "lastClean", "remainingSaniSolution"
            ]
            for key in direct_keys:
                add_or_update_sensor(key, device.get(key))

                    # Add sensors for 'operationStatus' (nested object)
            if "operationStatus" in device:
                operation_keys = ["state", "progress", "error"]
                for sub_key in operation_keys:
                    add_or_update_sensor(sub_key, device.get(sub_key))

            # Add sensors for 'configuration' (nested object)
            if "configuration" in device:
                configuration_keys = ["volumeLevel"]
                for sub_key in configuration_keys:
                    add_or_update_sensor(sub_key, device.get(sub_key))

        if new_entities:
            async_add_entities(new_entities)

    # Schedule initial update
    update_sensors()

    # Listen for coordinator updates
    coordinator.async_add_listener(update_sensors)
