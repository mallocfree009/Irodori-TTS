import unittest

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
        self.assertIn("uploaded_audio", input_types["optional"])

        # RETURN_TYPES Check
        self.assertEqual(node.RETURN_TYPES, ("AUDIO",))
        self.assertEqual(node.FUNCTION, "generate")

    def test_irodoritts_design_web_api_instantiation(self):
        node = IrodoriTTSDesignWebAPI()

        # INPUT_TYPES Check
        input_types = node.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("optional", input_types)
        self.assertIn("api_url", input_types["required"])
        self.assertIn("text", input_types["required"])
        self.assertIn("caption", input_types["optional"])

        # RETURN_TYPES Check
        self.assertEqual(node.RETURN_TYPES, ("AUDIO",))
        self.assertEqual(node.FUNCTION, "generate")

if __name__ == '__main__':
    unittest.main()
