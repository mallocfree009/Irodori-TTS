import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import shutil
import os

from gradio_app_voicedesign import _run_generation

class TestGradioAppVoiceDesignCleanup(unittest.TestCase):

    @patch("gradio_app_voicedesign.get_cached_runtime")
    @patch("gradio_app_voicedesign.save_audio")
    @patch("gradio_app_voicedesign.shutil.copy2")
    def test_run_generation_cleanup(self, mock_copy2, mock_save_audio, mock_get_cached_runtime):
        # Mocking runtime and result
        mock_runtime = MagicMock()
        mock_runtime.model_cfg.use_caption_condition = True
        mock_runtime.model_cfg.use_speaker_condition = False

        mock_result = MagicMock()
        mock_audio = MagicMock()
        mock_audio.float.return_value = mock_audio
        mock_result.audios = [mock_audio]
        mock_result.sample_rate = 24000
        mock_result.stage_timings = [("test", 0.1)]
        mock_result.total_to_decode = 0.1
        mock_result.used_seed = 42
        mock_result.messages = []
        mock_runtime.synthesize.return_value = mock_result
        mock_get_cached_runtime.return_value = (mock_runtime, False)

        mock_save_audio.return_value = "mock_saved_path.ogg"

        output_file_path = "test_out_voicedesign/custom_output.ogg"

        # Call with not_save_temp = True and output_file provided
        with patch("gradio_app_voicedesign.shutil.rmtree") as mock_rmtree, \
             patch("gradio_app_voicedesign._resolve_checkpoint_path") as mock_resolve:
            mock_resolve.return_value = "dummy.pt"
            result = _run_generation(
                checkpoint="dummy",
                model_device="cpu",
                model_precision="float32",
                codec_device="cpu",
                codec_precision="float32",
                enable_watermark=False,
                text="Hello",
                caption="Happy",
                num_steps=10,
                num_candidates=1,
                audio_format="ogg",
                seed_raw="",
                cfg_guidance_mode="independent",
                cfg_scale_text=3.0,
                cfg_scale_caption=4.0,
                cfg_scale_raw="",
                cfg_min_t=0.5,
                cfg_max_t=1.0,
                context_kv_cache=True,
                max_text_len_raw="",
                max_caption_len_raw="",
                truncation_factor_raw="",
                rescale_k_raw="",
                rescale_sigma_raw="",
                output_file=output_file_path,
                not_save_temp=True
            )

            mock_rmtree.assert_called_once()
            self.assertEqual(result[0]["value"], str(Path(output_file_path)))

        # Call with not_save_temp = False
        with patch("gradio_app_voicedesign.shutil.rmtree") as mock_rmtree, \
             patch("gradio_app_voicedesign._resolve_checkpoint_path") as mock_resolve:
            mock_resolve.return_value = "dummy.pt"
            result = _run_generation(
                checkpoint="dummy",
                model_device="cpu",
                model_precision="float32",
                codec_device="cpu",
                codec_precision="float32",
                enable_watermark=False,
                text="Hello",
                caption="Happy",
                num_steps=10,
                num_candidates=1,
                audio_format="ogg",
                seed_raw="",
                cfg_guidance_mode="independent",
                cfg_scale_text=3.0,
                cfg_scale_caption=4.0,
                cfg_scale_raw="",
                cfg_min_t=0.5,
                cfg_max_t=1.0,
                context_kv_cache=True,
                max_text_len_raw="",
                max_caption_len_raw="",
                truncation_factor_raw="",
                rescale_k_raw="",
                rescale_sigma_raw="",
                output_file=output_file_path,
                not_save_temp=False
            )

            mock_rmtree.assert_not_called()
            self.assertNotEqual(result[0]["value"], None)

if __name__ == "__main__":
    unittest.main()
