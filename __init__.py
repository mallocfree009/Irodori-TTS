from .nodes import MFIrodoriTTS, MFIrodoriTTSDesign

NODE_CLASS_MAPPINGS = {
    "MFIrodoriTTS": MFIrodoriTTS,
    "MFIrodoriTTSDesign": MFIrodoriTTSDesign,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MFIrodoriTTS": "MFIrodoriTTS",
    "MFIrodoriTTSDesign": "MFIrodoriTTSDesign (VoiceDesign)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
