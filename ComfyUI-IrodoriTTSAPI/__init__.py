from .comfy_nodes.nodes import IrodoriTTSWebAPI, IrodoriTTSDesignWebAPI

NODE_CLASS_MAPPINGS = {
    "IrodoriTTSWebAPI": IrodoriTTSWebAPI,
    "IrodoriTTSDesignWebAPI": IrodoriTTSDesignWebAPI,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IrodoriTTSWebAPI": "Irodori TTS Web API",
    "IrodoriTTSDesignWebAPI": "Irodori TTS VoiceDesign Web API",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
