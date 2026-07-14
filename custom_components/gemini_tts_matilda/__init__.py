"""Init for Gemini TTS Matilda."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, LOGGER

PLATFORMS = [Platform.TTS]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gemini TTS Matilda from a config entry."""
    try:
        from google import genai

        client = genai.Client(api_key=entry.data["api_key"])
        # Verify the API key works
        await client.aio.models.list()
        entry.runtime_data = client
    except Exception as exc:
        LOGGER.error("Failed to initialize Gemini client: %s", exc)
        raise ConfigEntryNotReady from exc

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)