from typing import Dict, Any, Literal
from pydantic import BaseModel
import os
import logging
from edgeroute.utils.device_profile import DeviceProfile
from edgeroute.utils.network import NetworkAwareness

logger = logging.getLogger(__name__)

class RoutingDecision(BaseModel):
    route: Literal["local", "cloud"]
    model: str
    reason: str
    fallback: Literal["cloud", "local"]

class RoutingDecisionAgent:
    def __init__(self):
        self.device = DeviceProfile()
        self.network = NetworkAwareness()
        
        # Default policy config (could be loaded from file)
        self.policy = {
            "MAX_LOCAL_COMPLEXITY": int(os.getenv("MAX_LOCAL_COMPLEXITY", 6)),
            "MAX_LOCAL_TOKENS": int(os.getenv("MAX_LOCAL_TOKENS", 1500)),
            "MIN_BANDWIDTH_MBPS": int(os.getenv("MIN_BANDWIDTH_MBPS", 5)),
            "COST_SAVING_MODE": os.getenv("COST_SAVING_MODE", "true").lower() == "true"
        }

    def decide(self, analysis: Dict[str, Any], preferred_model: str = None) -> RoutingDecision:
        device_info = self.device.get_profile()
        # network_info = self.network.get_network_metrics() # Can be slow, maybe skip for MVP or use async
        
        # Logic
        score = analysis.get("complexity_score", 0)
        tokens = analysis.get("estimated_tokens", 0)
        depth = analysis.get("reasoning_depth", "low")
        has_gpu = device_info.get("gpu", False)
        # bandwith = network_info.get("download_mbps", 0)

        # Default to local
        route = "local"
        reason = "Task fits local capability criteria."
        fallback = "cloud"
        
        # Preferred local models
        local_models = device_info.get("local_models", [])
        
        chosen_local_model = None
        
        # If user explicitly preferred a model, use it if it's "local" (or we might just trust them)
        if preferred_model:
             if preferred_model in local_models:
                 chosen_local_model = preferred_model
             else:
                 # If preferred model is not found, maybe they meant to route to it anyway? 
                 # Or maybe it's a cloud model.
                 # For safety, if they say 'gemma3:12b' and it's not found, we might warn or just try to use it.
                 # But let's assume if it is passed, we try to use it as the local option.
                 chosen_local_model = preferred_model

        if not chosen_local_model:
            # Auto-selection logic
            if "gemma3:12b" in local_models:
                chosen_local_model = "gemma3:12b"
            elif any("gemma" in m for m in local_models):
                chosen_local_model = next(m for m in local_models if "gemma" in m)
            elif "qwen2.5:3b" in local_models:
                chosen_local_model = "qwen2.5:3b"
            elif "llama3.2:3b" in local_models:
                chosen_local_model = "llama3.2:3b"
            elif local_models:
                chosen_local_model = local_models[0]
            else:
                chosen_local_model = "mistral:7b-instruct" # Fallback hope

        # Cloud models
        chosen_cloud_model = "gpt-4o" # or whatever AIsa maps

        # 1. Complexity Check
        if score > self.policy["MAX_LOCAL_COMPLEXITY"]:
            route = "cloud"
            reason = f"Complexity score {score} exceeds local limit {self.policy['MAX_LOCAL_COMPLEXITY']}."

        # 2. Token Check
        if tokens > self.policy["MAX_LOCAL_TOKENS"]:
            route = "cloud"
            reason = f"Token count {tokens} exceeds local limit {self.policy['MAX_LOCAL_TOKENS']}."

        # 3. Reasoning Depth Check
        if depth == "high":
            route = "cloud"
            reason = "High reasoning depth requires cloud model."
            
        # 4. Device Capability Override (if no local models or no RAM)
        if not local_models: # No local models found
             route = "cloud"
             reason = "No local models found on device."
             fallback = "local" # Technically fail, but keeping schema
        
        # 5. Cost Saving Override (if enabled, try to force local for borderline cases?)
        # For now, strict adherence to above rules.

        final_model = chosen_cloud_model if route == "cloud" else chosen_local_model

        return RoutingDecision(
            route=route,
            model=final_model,
            reason=reason,
            fallback=fallback
        )

if __name__ == "__main__":
    agent = RoutingDecisionAgent()
    sample_analysis = {
        "task_type": "general",
        "complexity_score": 7,
        "estimated_tokens": 100,
        "latency_sensitive": True,
        "requires_tools": False,
        "reasoning_depth": "medium"
    }
    print(agent.decide(sample_analysis).model_dump_json(indent=2))
