import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import torch

sys.path.insert(0, os.path.abspath("ComfyUI-IrodoriTTSAPI"))
from comfy_nodes.nodes import IrodoriTTSWebAPI, IrodoriTTSDesignWebAPI

class TestComfyUINodes(unittest.TestCase):
    def test_irodoritts_web_api_instantiation(self):
        node = IrodoriTTSWebAPI()

        # INPUT_TYPES Check
        input_types = node.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("optional", input_types)
        self.assertIn("api_url", input_types["required"])
        self.assertIn("text", input_types["required"])
        self.assertIn("seed", input_types["required"])
        self.assertNotIn("seed_raw", input_types["optional"])
        self.assertIn("uploaded_audio", input_types["optional"])
        self.assertEqual(input_types["required"]["model_device"][1]["default"], "cuda")
        self.assertEqual(input_types["required"]["codec_device"][1]["default"], "cuda")

        # RETURN_TYPES Check
        self.assertEqual(node.RETURN_TYPES, ("AUDIO", "DICT"))
        self.assertEqual(node.RETURN_NAMES, ("audio", "parameters"))
        self.assertEqual(node.FUNCTION, "generate")

    @patch("comfy_nodes.nodes.Client")
    @patch("comfy_nodes.nodes.torchaudio.load")
    @patch("comfy_nodes.nodes.os.remove")
    @patch("comfy_nodes.nodes.os.path.exists")
    @patch("builtins.print")
    def test_irodoritts_web_api_generate_file_deletion(self, mock_print, mock_exists, mock_remove, mock_torchaudio_load, mock_client_class):
        # モックの準備
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.predict.return_value = ({"value": "/dummy/path/audio.wav"}, "dummy_text", "dummy_timing")

        # torchaudio.load の戻り値のモック: (waveform, sample_rate)
        mock_waveform = torch.zeros(1, 1000)
        mock_torchaudio_load.return_value = (mock_waveform, 24000)

        # os.path.exists のモック
        mock_exists.return_value = True

        node = IrodoriTTSWebAPI()

        # 最低限の引数で呼び出し
        result = node.generate(
            api_url="http://dummy", checkpoint="dummy_ckpt", model_device="cpu", model_precision="fp32",
            codec_device="cpu", codec_precision="fp32", text="こんにちは", num_steps=10, num_candidates=1,
            cfg_guidance_mode="independent", cfg_scale_text=3.0, cfg_scale_speaker=5.0, cfg_min_t=0.5,
            cfg_max_t=1.0, context_kv_cache=True
        )

        # torchaudio.load が正しいパスで呼ばれたか
        mock_torchaudio_load.assert_called_once_with("/dummy/path/audio.wav", backend="soundfile")

        # os.remove が呼ばれ、ファイルが削除されたか
        mock_remove.assert_called_once_with("/dummy/path/audio.wav")

        # ログ出力が行われたか
        mock_print.assert_called_with("Deleted downloaded audio file: /dummy/path/audio.wav")

        # 結果の形式確認
        self.assertIn("waveform", result[0])
        self.assertEqual(result[0]["sample_rate"], 24000)

    def test_irodoritts_design_web_api_instantiation(self):
        node = IrodoriTTSDesignWebAPI()

        # INPUT_TYPES Check
        input_types = node.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("optional", input_types)
        self.assertIn("api_url", input_types["required"])
        self.assertIn("text", input_types["required"])
        self.assertIn("seed", input_types["required"])
        self.assertNotIn("seed_raw", input_types["optional"])
        self.assertIn("caption", input_types["optional"])
        self.assertEqual(input_types["required"]["model_device"][1]["default"], "cuda")
        self.assertEqual(input_types["required"]["codec_device"][1]["default"], "cuda")

        # RETURN_TYPES Check
        self.assertEqual(node.RETURN_TYPES, ("AUDIO", "DICT"))
        self.assertEqual(node.RETURN_NAMES, ("audio", "parameters"))
        self.assertEqual(node.FUNCTION, "generate")

    @patch("comfy_nodes.nodes.Client")
    @patch("comfy_nodes.nodes.torchaudio.load")
    @patch("comfy_nodes.nodes.os.remove")
    @patch("comfy_nodes.nodes.os.path.exists")
    @patch("builtins.print")
    def test_irodoritts_design_web_api_generate_file_deletion(self, mock_print, mock_exists, mock_remove, mock_torchaudio_load, mock_client_class):
        # モックの準備
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.predict.return_value = ({"value": "/dummy/path/design_audio.wav"}, "dummy_text", "dummy_timing")

        # torchaudio.load の戻り値のモック: (waveform, sample_rate)
        mock_waveform = torch.zeros(1, 1000)
        mock_torchaudio_load.return_value = (mock_waveform, 24000)

        # os.path.exists のモック
        mock_exists.return_value = True

        node = IrodoriTTSDesignWebAPI()

        # 最低限の引数で呼び出し
        result = node.generate(
            api_url="http://dummy", checkpoint="dummy_ckpt", model_device="cpu", model_precision="fp32",
            codec_device="cpu", codec_precision="fp32", text="こんにちは", num_steps=10, num_candidates=1,
            cfg_guidance_mode="independent", cfg_scale_text=2.0, cfg_scale_caption=4.0, cfg_min_t=0.5,
            cfg_max_t=1.0, context_kv_cache=True
        )

        # torchaudio.load が正しいパスで呼ばれたか
        mock_torchaudio_load.assert_called_once_with("/dummy/path/design_audio.wav", backend="soundfile")

        # os.remove が呼ばれ、ファイルが削除されたか
        mock_remove.assert_called_once_with("/dummy/path/design_audio.wav")

        # ログ出力が行われたか
        mock_print.assert_called_with("Deleted downloaded audio file: /dummy/path/design_audio.wav")

        # 結果の形式確認
        self.assertIn("waveform", result[0])
        self.assertEqual(result[0]["sample_rate"], 24000)

if __name__ == '__main__':
    unittest.main()
