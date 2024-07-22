"""Constants for the MadVR tests."""

from homeassistant.const import CONF_HOST, CONF_PORT

MOCK_CONFIG = {
    CONF_HOST: "192.168.1.1",
    CONF_PORT: 44077,
}

MOCK_MAC = "00:11:22:33:44:55"

TEST_CON_ERROR = ConnectionError("Connection failed")
TEST_IMP_ERROR = NotImplementedError("Not implemented")
TEST_FAILED_MSG = "Failed to turn"
TEST_FAILED_CMD = "Failed to send command"
