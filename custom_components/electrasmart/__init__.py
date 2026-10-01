"""The Electra Air Conditioner integration.

PATCHED local copy (overrides the core integration via custom_components).

Upstream bug: a single malformed device entry returned by Electra's cloud
API (missing the "deviceToken" field) crashes
``ElectraAirConditioner.__init__`` with an uncaught ``KeyError``. That
exception propagates out of ``api.fetch_devices()`` and fails config entry
setup for the WHOLE account, taking every AC offline even though only one
device's data was bad.

Tracked upstream at:
- https://github.com/home-assistant/core/issues/183846
- https://github.com/home-assistant/core/issues/183829

Fix: monkey-patch ``ElectraAirConditioner.__init__`` to tolerate a missing
``deviceToken`` (falls back to an empty string and logs a warning) instead
of crashing. A device with no token simply won't accept commands until
Electra's API returns a real token for it again; every other device on the
account keeps working normally. Everything else in this file is an
unmodified copy of the core integration.
"""

import logging

from electrasmart.api import ElectraAPI, ElectraApiError
from electrasmart.device import ElectraAirConditioner

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_IMEI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE]

type ElectraSmartConfigEntry = ConfigEntry[ElectraAPI]


def _patch_pyelectra_missing_device_token() -> None:
    """Make ElectraAirConditioner tolerant of a missing deviceToken."""
    original_init = ElectraAirConditioner.__init__

    def patched_init(self, data):  # noqa: ANN001, ANN202
        if "deviceToken" not in data:
            _LOGGER.warning(
                "Electra device %s is missing 'deviceToken' in the API "
                "response (upstream bug, see "
                "github.com/home-assistant/core/issues/183846); using an "
                "empty token so the rest of the integration keeps working. "
                "This device may not accept commands until Electra's API "
                "returns a real token for it",
                data.get("name", data.get("id", "unknown")),
            )
            data = {**data, "deviceToken": ""}
        original_init(self, data)

    ElectraAirConditioner.__init__ = patched_init


_patch_pyelectra_missing_device_token()


async def async_setup_entry(
    hass: HomeAssistant, entry: ElectraSmartConfigEntry
) -> bool:
    """Set up Electra Smart Air Conditioner from a config entry."""
    api = ElectraAPI(
        async_get_clientsession(hass), entry.data[CONF_IMEI], entry.data[CONF_TOKEN]
    )
    try:
        await api.fetch_devices()
    except ElectraApiError as exp:
        raise ConfigEntryNotReady(f"Error communicating with API: {exp}") from exp

    entry.async_on_unload(entry.add_update_listener(update_listener))
    entry.runtime_data = api
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ElectraSmartConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(
    hass: HomeAssistant, config_entry: ElectraSmartConfigEntry
) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)
