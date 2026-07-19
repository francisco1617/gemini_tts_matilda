"""Init for Gemini TTS Matilda."""

from google import genai

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, LOGGER

PLATFORMS = [Platform.TTS]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gemini TTS Matilda from a config entry."""
    try:
        # Crear el cliente fuera del event loop (SSL es bloqueante)
        client = await hass.async_add_executor_job(
            _create_client, entry.data["api_key"]
        )
        # models.list() sí es async
        await client.aio.models.list()
        entry.runtime_data = client
    except Exception as exc:
        LOGGER.error("Failed to initialize Gemini client: %s", exc)
        raise ConfigEntryNotReady from exc

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _create_client(api_key: str) -> genai.Client:
    """Create Gemini client (blocking SSL init, runs in executor)."""
    return genai.Client(api_key=api_key)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)