import unittest
import sys
import os

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
        self.assertEqual(node.RETURN_NAMES, ("audio", "params"))
        self.assertEqual(node.FUNCTION, "generate")

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
        self.assertEqual(node.RETURN_NAMES, ("audio", "params"))
        self.assertEqual(node.FUNCTION, "generate")

if __name__ == '__main__':
    unittest.main()
