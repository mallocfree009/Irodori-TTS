import os
import tempfile
import torchaudio
import torch
from gradio_client import Client, handle_file

class IrodoriTTSWebAPI:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_url": ("STRING", {"default": "http://127.0.0.1:7860/"}),
                "checkpoint": ("STRING", {"default": "Aratako/Irodori-TTS-500M-v2"}),
                "model_device": (["auto", "cuda", "cpu", "mps"], {"default": "cuda"}),
                "model_precision": (["fp32", "bf16", "fp16"], {"default": "fp32"}),
                "codec_device": (["auto", "cuda", "cpu", "mps"], {"default": "cuda"}),
                "codec_precision": (["fp32", "bf16", "fp16"], {"default": "fp32"}),
                "text": ("STRING", {"multiline": True}),
                "num_steps": ("INT", {"default": 40, "min": 1, "max": 120}),
                "num_candidates": ("INT", {"default": 1, "min": 1, "max": 32}),
                "cfg_guidance_mode": (["independent", "joint", "alternating"], {"default": "independent"}),
                "cfg_scale_text": ("FLOAT", {"default": 3.0, "step": 0.1}),
                "cfg_scale_speaker": ("FLOAT", {"default": 5.0, "step": 0.1}),
                "cfg_min_t": ("FLOAT", {"default": 0.5}),
                "cfg_max_t": ("FLOAT", {"default": 1.0}),
                "context_kv_cache": ("BOOLEAN", {"default": True}),
                "seed": ("INT", {"default": 0, "min": -1, "max": 0xffffffffffffffff}),
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

    RETURN_TYPES = ("AUDIO", "DICT")
    RETURN_NAMES = ("audio", "params")
    FUNCTION = "generate"
    CATEGORY = "IrodoriTTS"

    def generate(self, api_url, checkpoint, model_device, model_precision, codec_device, codec_precision, text, num_steps, num_candidates, cfg_guidance_mode, cfg_scale_text, cfg_scale_speaker, cfg_min_t, cfg_max_t, context_kv_cache, seed=0, uploaded_audio=None, cfg_scale_raw="", truncation_factor_raw="", rescale_k_raw="", rescale_sigma_raw="", speaker_kv_scale_raw="", speaker_kv_min_t_raw="0.9", speaker_kv_max_layers_raw=""):
        client = Client(src=api_url)

        params = {
            "api_url": api_url,
            "checkpoint": checkpoint,
            "model_device": model_device,
            "model_precision": model_precision,
            "codec_device": codec_device,
            "codec_precision": codec_precision,
            "text": text,
            "num_steps": num_steps,
            "num_candidates": num_candidates,
            "cfg_guidance_mode": cfg_guidance_mode,
            "cfg_scale_text": cfg_scale_text,
            "cfg_scale_speaker": cfg_scale_speaker,
            "cfg_min_t": cfg_min_t,
            "cfg_max_t": cfg_max_t,
            "context_kv_cache": context_kv_cache,
            "seed": seed,
            "cfg_scale_raw": cfg_scale_raw,
            "truncation_factor_raw": truncation_factor_raw,
            "rescale_k_raw": rescale_k_raw,
            "rescale_sigma_raw": rescale_sigma_raw,
            "speaker_kv_scale_raw": speaker_kv_scale_raw,
            "speaker_kv_min_t_raw": speaker_kv_min_t_raw,
            "speaker_kv_max_layers_raw": speaker_kv_max_layers_raw,
        }

        seed_raw = str(seed)

        audio_file_path = None
        if uploaded_audio is not None:
            # uploaded_audio is expected to be a dict: {"waveform": tensor, "sample_rate": int}
            waveform = uploaded_audio["waveform"]
            sample_rate = uploaded_audio["sample_rate"]
            if waveform.dim() == 3:
                # ComfyUI audio format: (batch, channels, samples)
                waveform = waveform.squeeze(0)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                audio_file_path = tmp_file.name

            # Use torchaudio.save with soundfile backend to avoid torchcodec dependency issues
            torchaudio.save(audio_file_path, waveform.cpu(), sample_rate, backend="soundfile")

            # Use handle_file for uploading
            uploaded_audio_arg = handle_file(audio_file_path)
        else:
            uploaded_audio_arg = None

        try:
            result = client.predict(
                checkpoint=checkpoint,
                model_device=model_device,
                model_precision=model_precision,
                codec_device=codec_device,
                codec_precision=codec_precision,
                text=text,
                uploaded_audio=uploaded_audio_arg,
                num_steps=num_steps,
                num_candidates=num_candidates,
                seed_raw=seed_raw,
                cfg_guidance_mode=cfg_guidance_mode,
                cfg_scale_text=cfg_scale_text,
                cfg_scale_speaker=cfg_scale_speaker,
                cfg_scale_raw=cfg_scale_raw,
                cfg_min_t=cfg_min_t,
                cfg_max_t=cfg_max_t,
                context_kv_cache=context_kv_cache,
                truncation_factor_raw=truncation_factor_raw,
                rescale_k_raw=rescale_k_raw,
                rescale_sigma_raw=rescale_sigma_raw,
                speaker_kv_scale_raw=speaker_kv_scale_raw,
                speaker_kv_min_t_raw=speaker_kv_min_t_raw,
                speaker_kv_max_layers_raw=speaker_kv_max_layers_raw,
                api_name="/generate"
            )
        finally:
            if audio_file_path and os.path.exists(audio_file_path):
                os.remove(audio_file_path)

        # Result is a tuple: (audio1, audio2, ..., audio32, detail_text, timing_text)
        # We take the first audio output (result[0])
        out_audio_path = result[0]
        if isinstance(out_audio_path, dict) and "value" in out_audio_path:
            out_audio_path = out_audio_path["value"]

        if out_audio_path is None:
            raise ValueError("API did not return a valid audio file.")

        waveform, sample_rate = torchaudio.load(out_audio_path, backend="soundfile")

        # ComfyUI format: {"waveform": (1, channels, samples), "sample_rate": sample_rate}
        waveform = waveform.unsqueeze(0)

        return ({"waveform": waveform, "sample_rate": sample_rate}, params)


class IrodoriTTSDesignWebAPI:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_url": ("STRING", {"default": "http://127.0.0.1:7861/"}),
                "checkpoint": ("STRING", {"default": "Aratako/Irodori-TTS-500M-v2-VoiceDesign"}),
                "model_device": (["auto", "cuda", "cpu", "mps"], {"default": "cuda"}),
                "model_precision": (["fp32", "bf16", "fp16"], {"default": "fp32"}),
                "codec_device": (["auto", "cuda", "cpu", "mps"], {"default": "cuda"}),
                "codec_precision": (["fp32", "bf16", "fp16"], {"default": "fp32"}),
                "text": ("STRING", {"multiline": True}),
                "num_steps": ("INT", {"default": 40, "min": 1, "max": 120}),
                "num_candidates": ("INT", {"default": 1, "min": 1, "max": 32}),
                "cfg_guidance_mode": (["independent", "joint", "alternating"], {"default": "independent"}),
                "cfg_scale_text": ("FLOAT", {"default": 2.0, "step": 0.1}),
                "cfg_scale_caption": ("FLOAT", {"default": 4.0, "step": 0.1}),
                "cfg_min_t": ("FLOAT", {"default": 0.5}),
                "cfg_max_t": ("FLOAT", {"default": 1.0}),
                "context_kv_cache": ("BOOLEAN", {"default": True}),
                "seed": ("INT", {"default": 0, "min": -1, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "caption": ("STRING", {"multiline": True, "default": ""}),
                "cfg_scale_raw": ("STRING", {"default": ""}),
                "max_text_len_raw": ("STRING", {"default": ""}),
                "max_caption_len_raw": ("STRING", {"default": ""}),
                "truncation_factor_raw": ("STRING", {"default": ""}),
                "rescale_k_raw": ("STRING", {"default": ""}),
                "rescale_sigma_raw": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("AUDIO", "DICT")
    RETURN_NAMES = ("audio", "params")
    FUNCTION = "generate"
    CATEGORY = "IrodoriTTS"

    def generate(self, api_url, checkpoint, model_device, model_precision, codec_device, codec_precision, text, num_steps, num_candidates, cfg_guidance_mode, cfg_scale_text, cfg_scale_caption, cfg_min_t, cfg_max_t, context_kv_cache, seed=0, caption="", cfg_scale_raw="", max_text_len_raw="", max_caption_len_raw="", truncation_factor_raw="", rescale_k_raw="", rescale_sigma_raw=""):
        client = Client(src=api_url)

        params = {
            "api_url": api_url,
            "checkpoint": checkpoint,
            "model_device": model_device,
            "model_precision": model_precision,
            "codec_device": codec_device,
            "codec_precision": codec_precision,
            "text": text,
            "num_steps": num_steps,
            "num_candidates": num_candidates,
            "cfg_guidance_mode": cfg_guidance_mode,
            "cfg_scale_text": cfg_scale_text,
            "cfg_scale_caption": cfg_scale_caption,
            "cfg_min_t": cfg_min_t,
            "cfg_max_t": cfg_max_t,
            "context_kv_cache": context_kv_cache,
            "seed": seed,
            "caption": caption,
            "cfg_scale_raw": cfg_scale_raw,
            "max_text_len_raw": max_text_len_raw,
            "max_caption_len_raw": max_caption_len_raw,
            "truncation_factor_raw": truncation_factor_raw,
            "rescale_k_raw": rescale_k_raw,
            "rescale_sigma_raw": rescale_sigma_raw,
        }

        seed_raw = str(seed)

        result = client.predict(
            checkpoint=checkpoint,
            model_device=model_device,
            model_precision=model_precision,
            codec_device=codec_device,
            codec_precision=codec_precision,
            text=text,
            caption=caption,
            num_steps=num_steps,
            num_candidates=num_candidates,
            seed_raw=seed_raw,
            cfg_guidance_mode=cfg_guidance_mode,
            cfg_scale_text=cfg_scale_text,
            cfg_scale_caption=cfg_scale_caption,
            cfg_scale_raw=cfg_scale_raw,
            cfg_min_t=cfg_min_t,
            cfg_max_t=cfg_max_t,
            context_kv_cache=context_kv_cache,
            max_text_len_raw=max_text_len_raw,
            max_caption_len_raw=max_caption_len_raw,
            truncation_factor_raw=truncation_factor_raw,
            rescale_k_raw=rescale_k_raw,
            rescale_sigma_raw=rescale_sigma_raw,
            api_name="/generate"
        )

        # Result is a tuple: (audio1, audio2, ..., audio32, detail_text, timing_text)
        out_audio_path = result[0]
        if isinstance(out_audio_path, dict) and "value" in out_audio_path:
            out_audio_path = out_audio_path["value"]

        if out_audio_path is None:
            raise ValueError("API did not return a valid audio file.")

        waveform, sample_rate = torchaudio.load(out_audio_path, backend="soundfile")

        # ComfyUI format: {"waveform": (1, channels, samples), "sample_rate": sample_rate}
        waveform = waveform.unsqueeze(0)

        return ({"waveform": waveform, "sample_rate": sample_rate}, params)
