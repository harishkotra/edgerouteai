from agno.agent import Agent
from agno.models.openai import OpenAIChat
from pydantic import BaseModel
import re

class ValidationResult(BaseModel):
    is_valid: bool
    reason: str
    retry_needed: bool

class ResponseValidatorAgent:
    def __init__(self):
        self.uncertainty_keywords = ["maybe", "I'm not sure", "possibly", "unclear", "cannot determine"]

    def validate(self, original_prompt: str, response_text: str, source: str) -> ValidationResult:
        """
        Validates the response based on heuristics.
        """
        # 1. Length Check
        if len(response_text) < 20: # Arbitrary threshold for "too short"
            return ValidationResult(
                is_valid=False,
                reason="Response too short",
                retry_needed=True
            )

        # 2. Uncertainty Check
        if any(kw in response_text.lower() for kw in self.uncertainty_keywords):
             return ValidationResult(
                is_valid=False,
                reason="Response contains uncertainty markers",
                retry_needed=True
            )
            
        # 3. Missing reasoning check (if prompt asked for it)
        # Simple heuristic: if prompt had 'because' or 'why' and response doesn't have 'because' or 'due to'...
        # This is brittle, so let's keep it simple.
        
        return ValidationResult(
            is_valid=True,
            reason="Passed validation checks",
            retry_needed=False
        )
