import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Gatekeeper:
    """
    Standardized Feature-Flagging (GK) utility.
    
    Inspired by Meta's Gatekeeper system, this utility allows for 'Safe Rollouts' 
    and 'Dark Launches' of new features without requiring code deployments.
    
    Resolution Hierarchy:
    1. Environment Variables (`GK_FEATURE_NAME`) - Highest priority (Infrastructure override).
    2. Internal Registry (`_flags`) - Default configuration (Code-defined state).
    
    Usage:
        if gk.is_enabled("NEW_ALGORITHM"):
            do_new_thing()
    """
    
    _flags: Dict[str, bool] = {
        "ENABLE_AGENTIC_DIGESTS": True,   # Use LLM agents for curation
        "STRICT_RESPONSE_VALIDATION": True, # Enforce Pydantic models in responses
        "USE_EXPERIMENTAL_RANKER": False,   # Experimental ranking algorithm
        "DEBUG_METADATA_EXPOSURE": False,   # Expose internal IDs in API
    }
    
    @classmethod
    def is_enabled(cls, feature_name: str, default: bool = False) -> bool:

        env_val = os.getenv(f"GK_{feature_name}")
        if env_val is not None:
            return env_val.lower() in ("true", "1", "yes")
            

        return cls._flags.get(feature_name, default)

    @classmethod
    def get_all_flags(cls) -> Dict[str, bool]:
        return {k: cls.is_enabled(k) for k in cls._flags}


gk = Gatekeeper
