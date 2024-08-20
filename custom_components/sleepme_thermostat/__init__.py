import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .sleepme import SleepMeClient
from .update_manager import SleepMeUpdateManager
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the SleepMe Thermostat component."""
    _LOGGER.debug("Starting async_setup for SleepMe Thermostat.")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SleepMe Thermostat from a config entry."""
    _LOGGER.debug("Starting async_setup_entry for SleepMe Thermostat.")

    api_url = entry.data.get("api_url")
    api_token = entry.data.get("api_token")
    device_id = entry.data.get("device_id")

    # Retrieve the additional device information
    firmware_version = entry.data.get("firmware_version")
    mac_address = entry.data.get("mac_address")
    model = entry.data.get("model")
    serial_number = entry.data.get("serial_number")

    _LOGGER.debug(f"API URL: {api_url}")
    _LOGGER.debug(f"API Token: {api_token}")
    _LOGGER.debug(f"Device ID: {device_id}")
    _LOGGER.debug(f"Firmware Version: {firmware_version}")
    _LOGGER.debug(f"MAC Address: {mac_address}")
    _LOGGER.debug(f"Model: {model}")
    _LOGGER.debug(f"Serial Number: {serial_number}")

    if not api_token or not device_id:
        _LOGGER.error("API token or device ID is missing from configuration.")
        return False

    # Initialize the SleepMe client and store it in hass.data for shared access
    sleepme_controller = SleepMeClient(api_url, api_token, device_id)
    hass.data[DOMAIN]["sleepme_controller"] = sleepme_controller

    # Create and store the update manager
    update_manager = SleepMeUpdateManager(hass, api_url, api_token, device_id)
    hass.data[DOMAIN][f"{device_id}_update_manager"] = update_manager

    # Trigger the initial data fetch
    await update_manager.async_config_entry_first_refresh()

    # Store the device information in hass.data for access by platforms
    hass.data[DOMAIN]["device_info"] = {
        "firmware_version": firmware_version,
        "mac_address": mac_address,
        "model": model,
        "serial_number": serial_number,
    }

    _LOGGER.debug(f"SleepMeClient and Update Manager initialized and stored in hass.data for device {device_id}.")

    # Forward the entry setup to the specific platforms, including the sensors platform
    await hass.config_entries.async_forward_entry_setups(entry, ["climate", "binary_sensor"])

    _LOGGER.info("SleepMe Thermostat component initialized successfully.")
    return True
