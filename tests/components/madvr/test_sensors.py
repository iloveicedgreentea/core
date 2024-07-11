"""Tests for the MadVR sensor entities."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from syrupy import SnapshotAssertion

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.entity_registry as er

from . import setup_integration
from .conftest import get_update_callback

from tests.common import MockConfigEntry, snapshot_platform


async def test_sensor_setup_and_states(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    mock_madvr_client: AsyncMock,
) -> None:
    """Test setup of the sensor entities and their states."""
    with patch("homeassistant.components.madvr.PLATFORMS", [Platform.SENSOR]):
        await setup_integration(hass, mock_config_entry)

    update_callback = get_update_callback(mock_madvr_client)

    # Create a big data update with all sensor values
    update_data = {
        "temp_gpu": 45.5,
        "temp_hdmi": 40.0,
        "temp_cpu": 50.2,
        "temp_mainboard": 35.8,
        "incoming_res": "3840x2160",
        "incoming_frame_rate": "60p",
        "outgoing_signal_type": "2D",
        "incoming_signal_type": "3D",
        "incoming_color_space": "RGB",
        "incoming_bit_depth": "10bit",
        "incoming_colorimetry": "2020",
        "incoming_black_levels": "PC",
        "incoming_aspect_ratio": "16:9",
        "outgoing_res": "3840x2160",
        "outgoing_frame_rate": "60p",
        "outgoing_color_space": "RGB",
        "outgoing_bit_depth": "10bit",
        "outgoing_colorimetry": "2020",
        "outgoing_black_levels": "PC",
        "aspect_res": "3840:2160",
        "aspect_dec": "1.78",
        "aspect_int": "178",
        "aspect_name": "Widescreen",
        "masking_res": "3840:2160",
        "masking_dec": "1.78",
        "masking_int": "178",
    }

    # Update all sensors at once
    update_callback(update_data)
    await hass.async_block_till_done()

    # Snapshot all entity states
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)

    # Test invalid temperature value
    update_callback({"temp_gpu": -1})
    await hass.async_block_till_done()
    assert hass.states.get("sensor.madvr_envy_gpu_temperature").state == "unknown"

    # Test sensor unavailability
    update_callback({"incoming_res": None})
    await hass.async_block_till_done()
    assert hass.states.get("sensor.madvr_envy_incoming_res").state == "unknown"

    # Test sensor becomes available again
    update_callback({"incoming_res": "1920x1080"})
    await hass.async_block_till_done()
    assert hass.states.get("sensor.madvr_envy_incoming_res").state == "1920x1080"
