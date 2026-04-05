import os
import torch
from pathlib import Path
from typing import Any, Dict, Tuple, Optional

from irodori_tts.inference_runtime import (
    RuntimeKey,
    SamplingRequest,
    default_runtime_device,
    get_cached_runtime,
    list_available_runtime_devices,
    list_available_runtime_precisions,
    clear_cached_runtime,
)

MAX_GRADIO_CANDIDATES = 32
FIXED_SECONDS = 30.0

def _get_default_checkpoint() -> str:
    candidates = sorted(
        [
            *Path(".").glob("**/checkpoint_*.pt"),
            *Path(".").glob("**/checkpoint_*.safetensors"),
        ]
    )
    if not candidates:
        return "Aratako/Irodori-TTS-500M-v2"
    return str(candidates[-1])

def _get_default_voicedesign_checkpoint() -> str:
    candidates = sorted(
        [
            *Path(".").glob("**/checkpoint_*.pt"),
            *Path(".").glob("**/checkpoint_*.safetensors"),
        ]
    )
    preferred = [
        path
        for path in candidates
        if "caption" in str(path).lower() or "voice_design" in str(path).lower()
    ]
    if preferred:
        return str(preferred[-1])
    if candidates:
        return str(candidates[-1])
    return "Aratako/Irodori-TTS-500M-v2-VoiceDesign"


def _build_runtime_key(
    checkpoint: str,
    model_device: str,
    model_precision: str,
    codec_device: str,
    codec_precision: str,
    enable_watermark: bool,
) -> RuntimeKey:
    # Resolve HF check if needed, but in ComfyUI local path is mostly used.
    # Fallback to direct string logic.
    return RuntimeKey(
        checkpoint=checkpoint,
        model_device=str(model_device),
        codec_repo="Aratako/Semantic-DACVAE-Japanese-32dim",
        model_precision=str(model_precision),
        codec_device=str(codec_device),
        codec_precision=str(codec_precision),
        enable_watermark=bool(enable_watermark),
        compile_model=False,
        compile_dynamic=False,
    )


class MFIrodoriTTS:
    @classmethod
    def INPUT_TYPES(s) -> Dict[str, Any]:
        device_choices = list_available_runtime_devices()
        default_model_device = default_runtime_device()
        model_precision_choices = list_available_runtime_precisions(default_model_device)

        return {
            "required": {
                "checkpoint": ("STRING", {"default": _get_default_checkpoint()}),
                "model_device": (device_choices, {"default": default_model_device}),
                "model_precision": (model_precision_choices, {"default": model_precision_choices[0]}),
                "codec_device": (device_choices, {"default": default_model_device}),
                "codec_precision": (model_precision_choices, {"default": model_precision_choices[0]}),
                "enable_watermark": ("BOOLEAN", {"default": False}),
                "text": ("STRING", {"multiline": True, "default": ""}),
                "num_steps": ("INT", {"default": 40, "min": 1, "max": 120}),
                "num_candidates": ("INT", {"default": 1, "min": 1, "max": MAX_GRADIO_CANDIDATES}),
                "seed_raw": ("STRING", {"default": ""}),
                "cfg_guidance_mode": (["independent", "joint", "alternating"], {"default": "independent"}),
                "cfg_scale_text": ("FLOAT", {"default": 3.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "cfg_scale_speaker": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "cfg_min_t": ("FLOAT", {"default": 0.5}),
                "cfg_max_t": ("FLOAT", {"default": 1.0}),
                "context_kv_cache": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "uploaded_audio": ("AUDIO",),
                "cfg_scale_raw": ("STRING", {"default": ""}),
                "truncation_factor_raw": ("STRING", {"default": ""}),
                "rescale_k_raw": ("STRING", {"default": ""}),
                "rescale_sigma_raw": ("STRING", {"default": ""}),
                "speaker_kv_scale_raw": ("STRING", {"default": ""}),
                "speaker_kv_min_t_raw": ("STRING", {"default": "0.9"}),
                "speaker_kv_max_layers_raw": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "generate"
    CATEGORY = "MFIrodoriTTS"

    def generate(
        self,
        checkpoint: str,
        model_device: str,
        model_precision: str,
        codec_device: str,
        codec_precision: str,
        enable_watermark: bool,
        text: str,
        num_steps: int,
        num_candidates: int,
        seed_raw: str,
        cfg_guidance_mode: str,
        cfg_scale_text: float,
        cfg_scale_speaker: float,
        cfg_min_t: float,
        cfg_max_t: float,
        context_kv_cache: bool,
        uploaded_audio: Optional[Dict[str, Any]] = None,
        cfg_scale_raw: str = "",
        truncation_factor_raw: str = "",
        rescale_k_raw: str = "",
        rescale_sigma_raw: str = "",
        speaker_kv_scale_raw: str = "",
        speaker_kv_min_t_raw: str = "0.9",
        speaker_kv_max_layers_raw: str = "",
    ) -> Tuple[Dict[str, Any]]:

        def _parse_float(raw: str) -> Optional[float]:
            text_val = raw.strip()
            if text_val == "" or text_val.lower() == "none":
                return None
            return float(text_val)

        def _parse_int(raw: str) -> Optional[int]:
            text_val = raw.strip()
            if text_val == "" or text_val.lower() == "none":
                return None
            return int(text_val)

        if str(text).strip() == "":
            raise ValueError("text is required.")

        runtime_key = _build_runtime_key(
            checkpoint, model_device, model_precision, codec_device, codec_precision, enable_watermark
        )
        runtime, _ = get_cached_runtime(runtime_key)

        cfg_scale = _parse_float(cfg_scale_raw)
        truncation_factor = _parse_float(truncation_factor_raw)
        rescale_k = _parse_float(rescale_k_raw)
        rescale_sigma = _parse_float(rescale_sigma_raw)
        speaker_kv_scale = _parse_float(speaker_kv_scale_raw)
        speaker_kv_min_t = _parse_float(speaker_kv_min_t_raw)
        speaker_kv_max_layers = _parse_int(speaker_kv_max_layers_raw)
        seed = _parse_int(seed_raw)

        # Handle uploaded_audio (ComfyUI audio is {'waveform': Tensor (B, C, L), 'sample_rate': int})
        # IrodoriTTS expects ref_wav path or ref_latent path. We can save the waveform to a temp file and pass it.
        # However, saving might be slow, so we can mock or adapt.
        # As an easier integration, let's write to a temp file if uploaded_audio is provided.
        ref_wav_path = None
        no_ref = True
        if uploaded_audio is not None and 'waveform' in uploaded_audio and 'sample_rate' in uploaded_audio:
            waveform = uploaded_audio['waveform'] # (B, C, L)
            sample_rate = uploaded_audio['sample_rate']
            # We take the first batch item
            import tempfile
            import torchaudio
            tmp_fd, ref_wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(tmp_fd)
            # Torchaudio expects (C, L)
            torchaudio.save(ref_wav_path, waveform[0], sample_rate)
            no_ref = False

        try:
            result = runtime.synthesize(
                SamplingRequest(
                    text=str(text),
                    ref_wav=ref_wav_path,
                    ref_latent=None,
                    no_ref=no_ref,
                    ref_normalize_db=-16.0,
                    ref_ensure_max=True,
                    num_candidates=num_candidates,
                    decode_mode="sequential",
                    seconds=FIXED_SECONDS,
                    max_ref_seconds=30.0,
                    max_text_len=None,
                    num_steps=num_steps,
                    seed=seed,
                    cfg_guidance_mode=cfg_guidance_mode,
                    cfg_scale_text=cfg_scale_text,
                    cfg_scale_speaker=cfg_scale_speaker,
                    cfg_scale=cfg_scale,
                    cfg_min_t=cfg_min_t,
                    cfg_max_t=cfg_max_t,
                    truncation_factor=truncation_factor,
                    rescale_k=rescale_k,
                    rescale_sigma=rescale_sigma,
                    context_kv_cache=context_kv_cache,
                    speaker_kv_scale=speaker_kv_scale,
                    speaker_kv_min_t=speaker_kv_min_t,
                    speaker_kv_max_layers=speaker_kv_max_layers,
                    trim_tail=True,
                ),
                log_fn=lambda x: print(x, flush=True)
            )

            # ComfyUI audio output: {"waveform": Tensor(B, C, L), "sample_rate": int}
            # result.audios is list of 1D tensors (L) or (C, L)? codec output is usually (1, L)
            waveforms = []
            for audio in result.audios:
                # Ensure shape (C, L)
                if audio.ndim == 1:
                    audio = audio.unsqueeze(0)
                waveforms.append(audio)

            # Stack into (B, C, L) where B is candidates
            if waveforms:
                # find max length to pad if varying length, but they might be same if seconds is fixed
                max_len = max(w.shape[1] for w in waveforms)
                padded_waveforms = []
                for w in waveforms:
                    if w.shape[1] < max_len:
                        pad = torch.zeros((w.shape[0], max_len - w.shape[1]), dtype=w.dtype, device=w.device)
                        padded_waveforms.append(torch.cat([w, pad], dim=1))
                    else:
                        padded_waveforms.append(w)
                out_tensor = torch.stack(padded_waveforms)
            else:
                out_tensor = torch.zeros((1, 1, int(FIXED_SECONDS * result.sample_rate)))

            return ({"waveform": out_tensor, "sample_rate": result.sample_rate},)
        finally:
            if ref_wav_path and os.path.exists(ref_wav_path):
                os.remove(ref_wav_path)


class MFIrodoriTTSDesign:
    @classmethod
    def INPUT_TYPES(s) -> Dict[str, Any]:
        device_choices = list_available_runtime_devices()
        default_model_device = default_runtime_device()
        model_precision_choices = list_available_runtime_precisions(default_model_device)

        return {
            "required": {
                "checkpoint": ("STRING", {"default": _get_default_voicedesign_checkpoint()}),
                "model_device": (device_choices, {"default": default_model_device}),
                "model_precision": (model_precision_choices, {"default": model_precision_choices[0]}),
                "codec_device": (device_choices, {"default": default_model_device}),
                "codec_precision": (model_precision_choices, {"default": model_precision_choices[0]}),
                "enable_watermark": ("BOOLEAN", {"default": False}),
                "text": ("STRING", {"multiline": True, "default": ""}),
                "caption": ("STRING", {"multiline": True, "default": ""}),
                "num_steps": ("INT", {"default": 40, "min": 1, "max": 120}),
                "num_candidates": ("INT", {"default": 1, "min": 1, "max": MAX_GRADIO_CANDIDATES}),
                "seed_raw": ("STRING", {"default": ""}),
                "cfg_guidance_mode": (["independent", "joint", "alternating"], {"default": "independent"}),
                "cfg_scale_text": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "cfg_scale_caption": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "cfg_min_t": ("FLOAT", {"default": 0.5}),
                "cfg_max_t": ("FLOAT", {"default": 1.0}),
                "context_kv_cache": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "cfg_scale_raw": ("STRING", {"default": ""}),
                "max_text_len_raw": ("STRING", {"default": ""}),
                "max_caption_len_raw": ("STRING", {"default": ""}),
                "truncation_factor_raw": ("STRING", {"default": ""}),
                "rescale_k_raw": ("STRING", {"default": ""}),
                "rescale_sigma_raw": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "generate"
    CATEGORY = "MFIrodoriTTS"

    def generate(
        self,
        checkpoint: str,
        model_device: str,
        model_precision: str,
        codec_device: str,
        codec_precision: str,
        enable_watermark: bool,
        text: str,
        caption: str,
        num_steps: int,
        num_candidates: int,
        seed_raw: str,
        cfg_guidance_mode: str,
        cfg_scale_text: float,
        cfg_scale_caption: float,
        cfg_min_t: float,
        cfg_max_t: float,
        context_kv_cache: bool,
        cfg_scale_raw: str = "",
        max_text_len_raw: str = "",
        max_caption_len_raw: str = "",
        truncation_factor_raw: str = "",
        rescale_k_raw: str = "",
        rescale_sigma_raw: str = "",
    ) -> Tuple[Dict[str, Any]]:

        def _parse_float(raw: str) -> Optional[float]:
            text_val = raw.strip()
            if text_val == "" or text_val.lower() == "none":
                return None
            return float(text_val)

        def _parse_int(raw: str) -> Optional[int]:
            text_val = raw.strip()
            if text_val == "" or text_val.lower() == "none":
                return None
            return int(text_val)

        if str(text).strip() == "":
            raise ValueError("text is required.")

        runtime_key = _build_runtime_key(
            checkpoint, model_device, model_precision, codec_device, codec_precision, enable_watermark
        )
        runtime, _ = get_cached_runtime(runtime_key)

        if not runtime.model_cfg.use_caption_condition:
            raise ValueError(
                "Loaded checkpoint does not enable caption conditioning. Use MFIrodoriTTS node for the original model."
            )

        cfg_scale = _parse_float(cfg_scale_raw)
        max_text_len = _parse_int(max_text_len_raw)
        max_caption_len = _parse_int(max_caption_len_raw)
        truncation_factor = _parse_float(truncation_factor_raw)
        rescale_k = _parse_float(rescale_k_raw)
        rescale_sigma = _parse_float(rescale_sigma_raw)
        seed = _parse_int(seed_raw)

        result = runtime.synthesize(
            SamplingRequest(
                text=str(text).strip(),
                caption=str(caption).strip() or None,
                ref_wav=None,
                ref_latent=None,
                no_ref=True,
                ref_normalize_db=-16.0,
                ref_ensure_max=True,
                num_candidates=num_candidates,
                decode_mode="sequential",
                seconds=FIXED_SECONDS,
                max_ref_seconds=30.0,
                max_text_len=max_text_len,
                max_caption_len=max_caption_len,
                num_steps=num_steps,
                seed=seed,
                cfg_guidance_mode=cfg_guidance_mode,
                cfg_scale_text=cfg_scale_text,
                cfg_scale_caption=cfg_scale_caption,
                cfg_scale_speaker=0.0,
                cfg_scale=cfg_scale,
                cfg_min_t=cfg_min_t,
                cfg_max_t=cfg_max_t,
                truncation_factor=truncation_factor,
                rescale_k=rescale_k,
                rescale_sigma=rescale_sigma,
                context_kv_cache=context_kv_cache,
                speaker_kv_scale=None,
                speaker_kv_min_t=None,
                speaker_kv_max_layers=None,
                trim_tail=True,
            ),
            log_fn=lambda x: print(x, flush=True)
        )

        waveforms = []
        for audio in result.audios:
            if audio.ndim == 1:
                audio = audio.unsqueeze(0)
            waveforms.append(audio)

        if waveforms:
            max_len = max(w.shape[1] for w in waveforms)
            padded_waveforms = []
            for w in waveforms:
                if w.shape[1] < max_len:
                    pad = torch.zeros((w.shape[0], max_len - w.shape[1]), dtype=w.dtype, device=w.device)
                    padded_waveforms.append(torch.cat([w, pad], dim=1))
                else:
                    padded_waveforms.append(w)
            out_tensor = torch.stack(padded_waveforms)
        else:
            out_tensor = torch.zeros((1, 1, int(FIXED_SECONDS * result.sample_rate)))

        return ({"waveform": out_tensor, "sample_rate": result.sample_rate},)
