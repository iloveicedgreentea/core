"""The jvc_projector integration."""

from __future__ import annotations

from jvcprojector.device import JvcProjectorAuthError
from jvcprojector.projector import JvcProjector, JvcProjectorConnectError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .coordinator import JvcProjectorDataUpdateCoordinator

type JVCConfigEntry = ConfigEntry[JvcProjectorDataUpdateCoordinator]

PLATFORMS = [Platform.BINARY_SENSOR, Platform.REMOTE, Platform.SELECT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: JVCConfigEntry) -> bool:
    """Set up integration from a config entry."""
    device = JvcProjector(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        password=entry.data[CONF_PASSWORD],
        timeout=1,
    )

    try:
        await device.connect(True)
    except JvcProjectorConnectError as err:
        await device.disconnect()
        raise ConfigEntryNotReady(
            f"Unable to connect to {entry.data[CONF_HOST]}"
        ) from err
    except JvcProjectorAuthError as err:
        await device.disconnect()
        raise ConfigEntryAuthFailed("Password authentication failed") from err

    coordinator = JvcProjectorDataUpdateCoordinator(hass, device)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    async def disconnect(event: Event) -> None:
        await device.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, disconnect)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: JVCConfigEntry) -> bool:
    """Unload config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.device.disconnect()
    return unload_ok
