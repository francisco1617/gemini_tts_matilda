"""Constants for the Gemini TTS Matilda integration."""

import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "gemini_tts_matilda"
DEFAULT_TITLE = "Gemini TTS Matilda"
DEFAULT_TTS_NAME = "Matilda TTS"

CONF_CHAT_MODEL = "chat_model"
RECOMMENDED_TTS_MODEL = "models/gemini-3.1-flash-tts-preview"
CONF_TEMPERATURE = "temperature"
RECOMMENDED_TEMPERATURE = 1.0

# The Director's Prompt — voice profile for Matilda
# Injected before every TTS call to give Gemini consistent character
CONF_TTS_PROMPT = "tts_prompt"
RECOMMENDED_TTS_PROMPT = """# AUDIO PROFILE: Matilda — pequeña hada de batalla mexicana

Tono: soprano agudo, dulce, suave, con aire aspirado.
Cadencia: fluctuante, melódica, vocales alargadas, siempre emocionada.
Actitud: inocente, asombrada, juguetona, siempre lista para pelear.

#### TRANSCRIPT
"""

RECOMMENDED_CONVERSATION_OPTIONS = {}
RECOMMENDED_TTS_OPTIONS = {}
