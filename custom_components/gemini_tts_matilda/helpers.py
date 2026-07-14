"""Helper classes for Gemini TTS Matilda integration."""

from contextlib import suppress
import io
import wave

from homeassistant.exceptions import HomeAssistantError

from .const import LOGGER


def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Generate a WAV file from Gemini TTS audio data.

    Args:
        audio_data: The raw audio data as a bytes object.
        mime_type: Mime type of the audio data.

    Returns:
        A bytes object representing the WAV file.

    """
    parameters = _parse_audio_mime_type(mime_type)

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(parameters["bits_per_sample"] // 8)
        wf.setframerate(parameters["rate"])
        wf.writeframes(audio_data)

    return wav_buffer.getvalue()


def _parse_audio_mime_type(mime_type: str) -> dict[str, int]:
    """Parse bits per sample and rate from an audio MIME type string.

    Args:
        mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

    Returns:
        A dictionary with "bits_per_sample" and "rate" keys.

    """
    if not mime_type.lower().startswith("audio/l"):
        LOGGER.warning("Received unexpected MIME type %s", mime_type)
        raise HomeAssistantError(f"Unsupported audio MIME type: {mime_type}")

    bits_per_sample = 16
    rate = 24000

    parts = mime_type.split(";")
    for param in parts:
        param = param.strip()
        if param.lower().startswith("rate="):
            with suppress(ValueError, IndexError):
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
        elif param.lower().startswith("audio/l"):
            with suppress(ValueError, IndexError):
                bits_per_sample = int(param.upper().split("L", 1)[1])

    return {"bits_per_sample": bits_per_sample, "rate": rate}
