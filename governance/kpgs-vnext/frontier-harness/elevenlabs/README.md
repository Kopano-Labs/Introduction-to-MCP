# ElevenLabs v0.4 — Governed Speech Modality Adapter

Status: **POC / live-capable / renderer-only**

This promotes the ElevenLabs leg of the Frontier Harness from a modality declaration to a live-capable text-to-speech renderer while preserving the KPGS semantic boundary.

## Authority boundary

```text
KPGS evaluated semantic output
        |
        v
kpgs.modality_contract.v1
        |
        +-- primary = speech
        +-- renderer = elevenlabs-speech
        +-- fallback = native-text
        +-- renderer_has_semantic_authority = false
        |
        v
short-lived capability lease
        |
        v
ElevenLabs TTS API
        |
        v
audio digest receipt
```

## Governing laws

1. **Modality != semantic authority.**
2. **Speech renderer != user consent.**
3. **Audio generation != canonical meaning.**
4. **A speech path must preserve a native text equivalent.**
5. **Private/restricted semantic text does not leave KPGS in v0.4.**
6. **API credentials remain external to repository and receipts.**

## Current provider policy

The balanced/low-latency default is `eleven_flash_v2_5`. `eleven_multilingual_v2` and `eleven_v3` are permitted alternatives for quality/expressiveness. Deprecated Turbo identifiers are not allow-listed.

The adapter uses `POST /v1/text-to-speech/{voice_id}` and injects the runtime API key only through the `xi-api-key` header.

## Gate

```bash
python governance/kpgs-vnext/frontier-harness/elevenlabs/validate_elevenlabs_adapter.py
```

The network-free validator proves exact lease scope, speech-only modality selection, required native-text fallback, external secret isolation, private-input rejection, audio digesting, and `renderer_has_semantic_authority=false`.

## Promotion boundary

A real speech generation is authorized only when KPGS has already evaluated the semantic content, the modality contract explicitly selects speech, a native-text fallback exists, the request is public/synthetic and externally shareable, a current scoped lease exists, and the external API key resolves at runtime.

The execution receipt records hashes and metadata, not raw text, audio, or credentials.
