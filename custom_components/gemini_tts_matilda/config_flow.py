"""Config flow for Gemini TTS Matilda."""

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_CHAT_MODEL,
    CONF_TEMPERATURE,
    CONF_TTS_PROMPT,
    DEFAULT_TITLE,
    DEFAULT_TTS_NAME,
    DOMAIN,
    LOGGER,
    RECOMMENDED_TTS_MODEL,
    RECOMMENDED_TTS_PROMPT,
)


class GeminiTTSMatildaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gemini TTS Matilda."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate the API key by doing a quick test
                from google import genai

                client = genai.Client(api_key=user_input["api_key"])
                await client.aio.models.list()

                # Create entry with the TTS prompt
                return self.async_create_entry(
                    title=DEFAULT_TITLE,
                    data={
                        "api_key": user_input["api_key"],
                        CONF_CHAT_MODEL: user_input.get(
                            CONF_CHAT_MODEL, RECOMMENDED_TTS_MODEL
                        ),
                        CONF_TEMPERATURE: user_input.get(
                            CONF_TEMPERATURE, 1.0
                        ),
                    },
                    options={
                        CONF_TTS_PROMPT: user_input.get(
                            CONF_TTS_PROMPT, RECOMMENDED_TTS_PROMPT
                        ),
                    },
                )
            except Exception as exc:
                LOGGER.error("API key validation failed: %s", exc)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_key"): str,
                    vol.Optional(
                        CONF_CHAT_MODEL, default=RECOMMENDED_TTS_MODEL
                    ): str,
                    vol.Optional(CONF_TEMPERATURE, default=1.0): vol.Coerce(float),
                    vol.Optional(
                        CONF_TTS_PROMPT, default=RECOMMENDED_TTS_PROMPT
                    ): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "api_key_url": "https://aistudio.google.com/app/apikey"
            },
        )