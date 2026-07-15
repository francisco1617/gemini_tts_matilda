"""Text to speech support for Gemini TTS Matilda.

Forked from home-assistant/core google_generative_ai_conversation/tts.py.
Modified to inject the Director's Prompt (CONF_TTS_PROMPT) before every TTS
call, giving Gemini a consistent voice character for Matilda.
"""

from collections.abc import Mapping
from typing import Any, override

from google.genai import types
from google.genai.errors import APIError, ClientError
from propcache.api import cached_property

from homeassistant.components.tts import (
    ATTR_VOICE,
    TextToSpeechEntity,
    TtsAudioType,
    Voice,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_CHAT_MODEL,
    CONF_TEMPERATURE,
    CONF_TTS_PROMPT,
    DOMAIN,
    LOGGER,
    RECOMMENDED_TEMPERATURE,
    RECOMMENDED_TTS_MODEL,
    RECOMMENDED_TTS_PROMPT,
)
from .helpers import convert_to_wav


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up TTS entities."""
    async_add_entities(
        [MatildaTTSEntity(config_entry)],
    )


class MatildaTTSEntity(TextToSpeechEntity, Entity):
    """Gemini TTS entity with Director's Prompt injection."""

    _attr_supported_options = [ATTR_VOICE, CONF_TTS_PROMPT]
    _attr_supported_languages = [
        "af-ZA", "am-ET", "ar-EG", "az-AZ", "be-BY", "bg-BG", "bn-BD",
        "ca-ES", "ceb-PH", "cmn-CN", "cs-CZ", "da-DK", "de-DE", "el-GR",
        "en-IN", "en-US", "es-ES", "es-US", "et-EE", "eu-ES", "fa-IR",
        "fi-FI", "fil-PH", "fr-FR", "gl-ES", "gu-IN", "he-IL", "hi-IN",
        "hr-HR", "ht-HT", "hu-HU", "hy-AM", "id-ID", "is-IS", "it-IT",
        "ja-JP", "jv-ID", "ka-GE", "kn-IN", "ko-KR", "kok-IN", "la-VA",
        "lb-LU", "lo-LA", "lt-LT", "lv-LV", "mai-IN", "mg-MG", "mk-MK",
        "ml-IN", "mn-MN", "mr-IN", "ms-MY", "my-MM", "nb-NO", "ne-NP",
        "nl-NL", "nn-NO", "or-IN", "pa-IN", "pl-PL", "ps-AF", "pt-BR",
        "pt-PT", "ro-RO", "ru-RU", "sd-PK", "si-LK", "sk-SK", "sl-SI",
        "sq-AL", "sr-RS", "sv-SE", "sw-KE", "ta-IN", "te-IN", "th-TH",
        "tr-TR", "uk-UA", "ur-PK", "vi-VN",
    ]
    _attr_default_language = "en-US"

    _supported_voices = [
        Voice(voice.split(" ", 1)[0].lower(), voice)
        for voice in (
            "Zephyr (Bright)", "Puck (Upbeat)", "Charon (Informative)",
            "Kore (Firm)", "Fenrir (Excitable)", "Leda (Youthful)",
            "Orus (Firm)", "Aoede (Breezy)", "Callirrhoe (Easy-going)",
            "Autonoe (Bright)", "Enceladus (Breathy)", "Iapetus (Clear)",
            "Umbriel (Easy-going)", "Algieba (Smooth)", "Despina (Smooth)",
            "Erinome (Clear)", "Algenib (Gravelly)", "Rasalgethi (Informative)",
            "Laomedeia (Upbeat)", "Achernar (Soft)", "Alnilam (Firm)",
            "Schedar (Even)", "Gacrux (Mature)", "Pulcherrima (Forward)",
            "Achird (Friendly)", "Zubenelgenubi (Casual)",
            "Vindemiatrix (Gentle)", "Sadachbia (Lively)",
            "Sadaltager (Knowledgeable)", "Sulafat (Warm)",
        )
    ]

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the TTS entity."""
        self.config_entry = config_entry
        self._genai_client = config_entry.runtime_data
        self._attr_name = config_entry.title
        self._attr_unique_id = config_entry.entry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=config_entry.title,
            manufacturer="Google",
            model=RECOMMENDED_TTS_MODEL.split("/")[-1],
            entry_type=dr.DeviceEntryType.SERVICE,
        )

    @callback
    @override
    def async_get_supported_voices(self, language: str) -> list[Voice]:
        """Return a list of supported voices for a language."""
        return self._supported_voices

    @cached_property
    @override
    def default_options(self) -> Mapping[str, Any]:
        """Return a mapping with the default options."""
        return {
            ATTR_VOICE: self._supported_voices[0].voice_id,
            CONF_TTS_PROMPT: RECOMMENDED_TTS_PROMPT,
        }

    @override
    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Load tts audio file from the engine.

        Injects the Director's Prompt (CONF_TTS_PROMPT) before the message
        to give Gemini consistent voice character for Matilda.
        """
        config = types.GenerateContentConfig()
        config.temperature = self.config_entry.options.get(
            CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE
        )
        config.response_modalities = ["AUDIO"]
        config.speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=options[ATTR_VOICE]
                )
            )
        )

        # === KEY MODIFICATION: inject Director's Prompt before message ===
        prompt = options.get(CONF_TTS_PROMPT) or self.config_entry.options.get(
            CONF_TTS_PROMPT, RECOMMENDED_TTS_PROMPT
        )
        full_message = prompt + "\n" + message if prompt else message

        def _extract_audio_parts(
            response: types.GenerateContentResponse,
        ) -> tuple[bytes, str]:
            if (
                not response.candidates
                or not response.candidates[0].content
                or not response.candidates[0].content.parts
                or not response.candidates[0].content.parts[0].inline_data
            ):
                raise ValueError("No content returned from TTS generation")

            data = response.candidates[0].content.parts[0].inline_data.data
            mime_type = response.candidates[0].content.parts[0].inline_data.mime_type

            if not isinstance(data, bytes):
                raise TypeError(
                    f"Expected bytes for audio data, got {type(data).__name__}"
                )
            if not isinstance(mime_type, str):
                raise TypeError(
                    f"Expected str for mime_type, got {type(mime_type).__name__}"
                )

            return data, mime_type

        try:
            response = await self._genai_client.aio.models.generate_content(
                model=self.config_entry.options.get(
                    CONF_CHAT_MODEL, RECOMMENDED_TTS_MODEL
                ),
                contents=full_message,
                config=config,
            )

            data, mime_type = _extract_audio_parts(response)
        except (APIError, ClientError, ValueError, TypeError) as exc:
            LOGGER.error("Error during TTS: %s", exc, exc_info=True)
            raise HomeAssistantError(exc) from exc

        return "wav", convert_to_wav(data, mime_type)