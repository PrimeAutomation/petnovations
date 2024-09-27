from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

class PetnovationsSensor(CoordinatorEntity):
    """Representation of a Petnovations sensor."""

    def __init__(self, coordinator, device, key, sub_key, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.device = device
        self.key = key
        self.sub_key = sub_key
        self._attr_name = name

        diagnostic_class = ["Operation Error", "Network Status", "Low Heater", "Fan Shutter"]
        sensors_class = ["Last Clean", "Remaining Cycles"]
        configuration_class = []
        controls_class = []

        if name in diagnostic_class:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        elif name in configuration_class:
            self._attr_entity_category = EntityCategory.CONFIG
        elif name in controls_class:
            self._attr_entity_category = EntityCategory.CONFIG
        else:
            self._attr_entity_category = None

        # Determine the unique ID
        if sub_key:
            unique_key = f"{device.get('manufacturerId', 'unknown')}_{key}_{sub_key}"
        else:
            unique_key = f"{device.get('manufacturerId', 'unknown')}_{key}"
        
        self._attr_unique_id = unique_key

        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.get("manufacturerId", "unknown"))},
            "name": device.get("name", "Unknown"),
            "manufacturer": "Petnovations",
            "model": "CatGenie A.I.",
            "sw_version": device.get("fwVersion", "Unknown"),
            "hw_version": device.get("hwRevision", "Unknown"),
            "serial_number": device.get("manufacturerId", "Unknown"),
            "via_device": device.get("macAddress", "Unknown"),
            "connections": {
                ("mac", device.get("macAddress", "Unknown")),
                ("bluetooth", device.get("bleConnectionId", "Unknown"))
            }
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return "Unknown"

        device = next((d for d in data.get("thingList", []) if d.get("manufacturerId") == self.device.get("manufacturerId")), None)
        if not device:
            return "Unknown"

        if self.key == "operationStatus":
            return device.get("operationStatus", {}).get(self.sub_key, "Unknown")
        elif self.key == "configuration":
            return device.get("configuration", {}).get(self.sub_key, "Unknown")
        else:
            return device.get(self.key, "Unknown")

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the CatGenie sensors based on a config entry."""
    coordinator = hass.data[entry.domain].get(entry.entry_id)
    if not coordinator:
        _LOGGER.error("Coordinator not found for entry_id %s", entry.entry_id)
        return

    data = coordinator.data
    sensors = []

    for device in data.get("thingList", []):
        sensors.append(PetnovationsSensor(coordinator, device, 'name', None, f"{device['name']} Name"))
        sensors.append(PetnovationsSensor(coordinator, device, 'macAddress', None, f"{device['name']} MAC Address"))
        sensors.append(PetnovationsSensor(coordinator, device, 'manufacturerId', None, f"{device['name']} Serial Number"))
        sensors.append(PetnovationsSensor(coordinator, device, 'bleConnectionId', None, f"{device['name']} BLE Address"))
        sensors.append(PetnovationsSensor(coordinator, device, 'lastClean', None, f"{device['name']} Last Clean"))
        sensors.append(PetnovationsSensor(coordinator, device, 'totalSaniSolution', None, f"{device['name']} Total Solution"))
        sensors.append(PetnovationsSensor(coordinator, device, 'remainingSaniSolution', None, f"{device['name']} Remaining Solution"))
        sensors.append(PetnovationsSensor(coordinator, device, 'usedSaniSolution', None, f"{device['name']} Used Solution"))
        sensors.append(PetnovationsSensor(coordinator, device, 'reportedStatus', None, f"{device['name']} Network Status"))
        sensors.append(PetnovationsSensor(coordinator, device, 'lowHeater', None, f"{device['name']} Low Heater"))
        sensors.append(PetnovationsSensor(coordinator, device, 'fanShutter', None, f"{device['name']} Fan Shutter"))
        sensors.append(PetnovationsSensor(coordinator, device, 'connectionMode', None, f"{device['name']} Network Type"))

        if "operationStatus" in device:

            sensors.append(PetnovationsSensor(coordinator, device, 'operationStatus', 'state', f"{device['name']} Operation Status"))
            sensors.append(PetnovationsSensor(coordinator, device, 'operationStatus', 'progress', f"{device['name']} Operation Progress"))
            sensors.append(PetnovationsSensor(coordinator, device, 'operationStatus', 'error', f"{device['name']} Operation Error"))

        if "configuration" in device:
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'volumeLevel', f"{device['name']} Volume Level"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'childLock', f"{device['name']} Panel Lock"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'childLock', f"{device['name']} Panel Lock Delay"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'extraDry' , f"{device['name']} Extra Dry"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'catDelay' , f"{device['name']} Cat Activation Delay"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'catSense' , f"{device['name']} Cat Sensitivity"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'schedule' , f"{device['name']} Scheduled Cycles"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'mode' , f"{device['name']} Operating Mode"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'manual' , f"{device['name']} Manual Mode"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'manual' , f"{device['name']} Manual Mode"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'dndFrom' , f"{device['name']} No Runtime Start"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'dndTo' , f"{device['name']} No Runtime End"))
            

            if "binaryElements" in device:
                sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'extraWash' , f"{device['name']} Extra Wash"))
                sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'extraShake' , f"{device['name']} Extra Shake"))

            if "heater" in device:
                sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'header_tempOutRef' , f"{device['name']} Extra Shake"))

    async_add_entities(sensors, True)
