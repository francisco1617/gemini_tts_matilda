# Gemini TTS Matilda

Custom Home Assistant integration for Google Gemini TTS with **Director's Prompt** injection.

Gives Gemini a consistent voice character for every TTS call — no more flat, neutral speech.

## What it does

This integration wraps the official Google Gemini TTS API and injects a **Director's Prompt** (voice character profile) before every text-to-speech request. The prompt controls tone, timbre, cadence, and attitude so your assistant sounds like the same character every time.

## Installation

### HACS (recommended)
1. Open HACS → Integrations → ⋮ (3 dots) → Custom repositories
2. Add `https://github.com/francisco1617/gemini_tts_matilda` as Integration
3. Search "Gemini TTS Matilda" and download
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration → Gemini TTS Matilda

### Manual
1. Copy `custom_components/gemini_tts_matilda/` to your HA `config/custom_components/`
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services

## Configuration

| Field | Description | Default |
|---|---|---|
| API Key | Your Google AI Studio API key | Required |
| TTS Model | Gemini TTS model to use | `models/gemini-3.1-flash-tts-preview` |
| Temperature | Creativity for voice (0.0-2.0) | 1.0 |
| Director's Prompt | Voice character profile injected before every TTS | Matilda's voice profile |

## Director's Prompt

The default prompt is Matilda's voice profile:

```
# AUDIO PROFILE: Matilda — pequeña hada de batalla mexicana

Tono y Timbre: Extremadamente agudo (soprano), dulce, suave y con un ligero
toque de aire (voz aspirada).

Cadencia y Ritmo: Fluctuante, melódica y propensa a alargamientos en las
vocales, siempre está emocionada.

Intención/Actitud: Inocente, asombrada, extremadamente juguetona. Siempre
suena como si estuviera lista para pelear o a la defensiva.

#### TRANSCRIPT
```

You can customize this to any character you want.

## Voices

30 Gemini voices available. Recommended: `Kore` (Firm), `Aoede` (Breezy), `Puck` (Upbeat).

## License

MIT