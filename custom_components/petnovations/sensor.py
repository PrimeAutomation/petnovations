from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from datetime import datetime, timedelta, timezone
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

        if self.key == "usedSaniSolution":
            operation_mode = device.get("configuration", {}).get("mode", "Unknown")
            manual_mode = device.get("configuration", {}).get("manual", "Unknown")
            if operation_mode == 0 and manual_mode == 0:
                cycles = (device.get(self.key, 0) / 240) * 450
                return f"{cycles}oz"
            else:
                cycles = (device.get(self.key, 0) / 120) * 450
                return f"{cycles}oz"

        elif self.key == "totalSaniSolution" or self.key == "remainingSaniSolution":
                count = device.get(self.key, "0")
                if count == 0:
                    return f"Depleted"
                elif count == 1:
                    return f"1 Cycle"
                else:
                    return f"{device.get(self.key, "0")} Cycles"


        elif self.key == "lastClean":
            last_clean_timestamp = device.get("lastClean", None)
            if last_clean_timestamp:
                return time_ago(last_clean_timestamp)
            else:
                return "Unknown"

        elif self.key == "operationStatus":
            if self.sub_key == "state":
                operation_status = device.get(self.key, {}).get(self.sub_key, 0)
                if operation_status == 0:
                    return f"Idle"
                elif operation_status == 1:
                    return f"Cleaning"
                elif operation_status == 2:
                    return f"Paused"
                else:
                    return f"Unknown"
                
            elif self.sub_key == "progress":
                operation_state = device.get(self.key, {}).get("state", 0)
                if operation_state == 0:
                    return f"Idle"
                else:
                    return f"{device.get(self.key, {}).get(self.sub_key, 0)}% Completed"

            elif self.sub_key == "error":
                err = device.get(self.key, {}).get(self.sub_key, None)
                return f"{err}"

        elif self.key == "configuration":

            # Is the CatGenie in Manual Mode?
            if self.sub_key == "manual" or self.sub_key == "childLock":
                if device.get("configuration", {}).get(self.sub_key, 0) == 1:
                    return f"Enabled"
                else:
                    return f"Disabled"

            elif self.sub_key == "mode":
                operation_mode = device.get(self.key, {}).get(self.sub_key, 0)
                if device.get("configuration", {}).get("manual", 0) == 1:
                    return f"Manual Activation"
                elif device.get(self.key, {}).get(self.sub_key, 0) == 0:
                    return f"Cat Activation"
                elif device.get(self.key, {}).get(self.sub_key, 0) == 1:
                    return f"Time Activation"
                else:
                    return device.get(self.key, self.sub_key, "Unknown")

            # Work in Progress - Do Not Disturb (To and From)

            elif self.sub_key == "do_not_disturb":
                dndFrom = device.get(self.key, {}).get("dndFrom", "00:00")
                dndTo = device.get(self.key, {}).get("dndTo", "00:00")
                timezone = device.get(self.key, {}).get("timezone", "-00:00")
                dstFrom = device.get(self.key, {}).get("dstFrom", "03-10 08:00:00")
                dstTo = device.get(self.key, {}).get("dstTo", "11-03 07:00:00")
                
                dndFrom_adjusted = adjust_time_for_timezone(dndFrom, timezone, dstFrom, dstTo)
                dndTo_adjusted = adjust_time_for_timezone(dndTo, timezone, dstFrom, dstTo)

                return f"{dndFrom_adjusted} to {dndTo_adjusted}"

            # Define Cat Activation Delay
            elif self.sub_key == "catDelay" or self.sub_key == "autoLock":
                # Convert activation delay from seconds to minutes
                delay = device.get(self.key, {}).get(self.sub_key, 0)
                minutes = int(delay / 60)
                # Return the value with "minute" or "minutes"
                if minutes == 0:
                    return f"Disabled"
                if minutes == 1:
                    return f"{minutes} minute"
                else:
                    return f"{minutes} minutes"
            else:
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
        sensors.append(PetnovationsSensor(coordinator, device, 'macAddress', None, f"{device['name']} MAC Address"))
        sensors.append(PetnovationsSensor(coordinator, device, 'manufacturerId', None, f"{device['name']} Serial Number"))
        sensors.append(PetnovationsSensor(coordinator, device, 'bleConnectionId', None, f"{device['name']} BLE Address"))
        sensors.append(PetnovationsSensor(coordinator, device, 'lastClean', None, f"{device['name']} Last Clean"))
        sensors.append(PetnovationsSensor(coordinator, device, 'totalSaniSolution', None, f"{device['name']} Cartridge Capacity"))
        sensors.append(PetnovationsSensor(coordinator, device, 'remainingSaniSolution', None, f"{device['name']} Cartridge Remaining"))
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
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'autoLock', f"{device['name']} Panel Lock Delay"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'extraDry' , f"{device['name']} Extra Dry"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'catDelay' , f"{device['name']} Cat Activation Delay"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'catSense' , f"{device['name']} Cat Sensitivity"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'schedule' , f"{device['name']} Scheduled Cycles"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'mode' , f"{device['name']} Operating Mode"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'manual' , f"{device['name']} Manual Mode"))
            sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'do_not_disturb' , f"{device['name']} Do Not Disturb"))
            

            if "binaryElements" in device:
                sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'extraWash' , f"{device['name']} Extra Wash"))
                sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'extraShake' , f"{device['name']} Extra Shake"))

            if "heater" in device:
                sensors.append(PetnovationsSensor(coordinator, device, 'configuration', 'heater_tempOutRef' , f"{device['name']} Heater Temperature Output"))

    async_add_entities(sensors, True)

def adjust_time_for_timezone(time_str, timezone_offset, dst_from, dst_to):
    from datetime import datetime, timedelta

    # If the time string is empty, return a default value or log a warning
    if not time_str:
        _LOGGER.warning(f"Invalid time string: {time_str}. Returning default value '00:00'.")
        return "00:00"  # Return a default time if the string is empty

    # Attempt to parse the time string, trying with and without seconds
    try:
        dnd_time = datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        dnd_time = datetime.strptime(time_str, "%H:%M")

    # Parse the timezone offset
    offset_hours, offset_minutes = map(int, timezone_offset.split(":"))
    offset = timedelta(hours=offset_hours, minutes=offset_minutes)

    # Apply the timezone offset
    adjusted_time = dnd_time + offset

    # Get the current date
    now = datetime.now()

    # Parse dstFrom and dstTo
    dst_start = datetime.strptime(dst_from, "%m-%d %H:%M:%S").replace(year=now.year)
    dst_end = datetime.strptime(dst_to, "%m-%d %H:%M:%S").replace(year=now.year)

    # If current date is within DST range, adjust for DST (add 1 hour)
    if dst_start <= now <= dst_end:
        adjusted_time += timedelta(hours=1)

    return adjusted_time.strftime("%H:%M")

def time_ago(timestamp):
    """Converts a timestamp to 'X minutes/hours/days ago' format."""
    # Convert the string timestamp to a datetime object
    try:
        past_time = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
    except ValueError:
        return "Invalid timestamp"
    
    # Get the current time in UTC
    current_time = datetime.now(timezone.utc)
    
    # Calculate the time difference
    time_difference = current_time - past_time
    
    # Convert the difference to minutes, hours, and days
    minutes = int(time_difference.total_seconds() / 60)
    hours = int(minutes / 60)
    days = int(hours / 24)
    
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        return f"{days} day{'s' if days != 1 else ''} ago"
