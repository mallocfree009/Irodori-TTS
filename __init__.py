import sys
from pathlib import Path

# ComfyUI dynamically loads this file, which means it might not have the parent directory in sys.path
# Therefore, we add the current directory to sys.path to allow absolute imports or make absolute import work.
sys.path.insert(0, str(Path(__file__).parent))

from comfyui_irodori_tts.nodes import MFIrodoriTTS, MFIrodoriTTSDesign

NODE_CLASS_MAPPINGS = {
    "MFIrodoriTTS": MFIrodoriTTS,
    "MFIrodoriTTSDesign": MFIrodoriTTSDesign,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MFIrodoriTTS": "MFIrodoriTTS",
    "MFIrodoriTTSDesign": "MFIrodoriTTSDesign (VoiceDesign)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
