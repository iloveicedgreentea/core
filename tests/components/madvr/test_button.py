"""Tests for the MadVR button entities."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from syrupy import SnapshotAssertion

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.components.madvr.const import ButtonCommands
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.entity_registry as er

from . import setup_integration

from tests.common import MockConfigEntry, snapshot_platform


async def test_button_setup_and_states(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    mock_madvr_client: AsyncMock,
) -> None:
    """Test setup of the button entities and their actions."""
    with patch("homeassistant.components.madvr.PLATFORMS", [Platform.BUTTON]):
        await setup_integration(hass, mock_config_entry)

    # Snapshot all entity states
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)

    # test a button press
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {
            ATTR_ENTITY_ID: "button.madvr_envy_open_profiles_menu",
        },
        blocking=True,
    )
    # ensure that pressing a button adds it to the queue
    mock_madvr_client.add_command_to_queue.assert_called_once_with(
        ButtonCommands.openmenu_profiles.value
    )
