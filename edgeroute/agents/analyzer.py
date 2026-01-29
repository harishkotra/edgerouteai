from agno.agent import Agent
from agno.models.openai import OpenAIChat 
from pydantic import BaseModel, Field
from typing import Literal
import json
from edgeroute.utils.complexity import ComplexityScorer

class TaskAnalysis(BaseModel):
    task_type: str = Field(..., description="Type of the task (e.g., summary, coding, creative, reasoning)")
    complexity_score: int = Field(..., description="Score from 1-10 indicating difficulty")
    estimated_tokens: int = Field(..., description="Estimated input token count")
    latency_sensitive: bool = Field(..., description="Whether the user needs an immediate response")
    requires_tools: bool = Field(..., description="If the task needs external tools (search, calculation)")
    reasoning_depth: Literal["low", "medium", "high"] = Field(..., description="Required depth of reasoning")

class TaskAnalyzerAgent:
    def __init__(self):
        # We can use a lightweight local model for analysis if available, or a fast cloud model.
        # For this design, we'll try to use a local model (e.g. llama3.2:1b) if possible to keep it "edge-first",
        # but since we are orchestrating, let's assume we run this logic in python first (heuristics) 
        # for maximum speed/low cost, and maybe use an LLM only if ambiguous.
        # The prompt implies this is an "Agent", so let's make it an Agno agent.
        # However, to save cost/time, we can implement the core logic deterministically using our detailed ComplexityScorer.
        
        self.scorer = ComplexityScorer()
        
        # Agno Agent definition (using a fast model, maybe the local one itself)
        # But wait, if we use a local model to decide whether to use a local model, we might deadlock on resource.
        # Let's trust the python scorer for now as the primary "brain" of this agent.
        pass

    def analyze(self, prompt: str) -> dict:
        # Hybrid approach: efficient python heuristics first.
        
        complexity_metrics = self.scorer.calculate_complexity(prompt)
        
        # Heuristic for task type (simple keyword matching)
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["summarize", "tldr", "shorten"]):
            task_type = "summary"
        elif any(w in prompt_lower for w in ["code", "function", "script", "api", "bug", "error"]):
            task_type = "coding"
        elif any(w in prompt_lower for w in ["design", "plan", "roadmap"]):
            task_type = "planning"
        else:
            task_type = "general"

        requires_tools = any(w in prompt_lower for w in ["search", "weather", "latest", "stock"])
        
        # Determine latency sensitivity (defaults to True unless deep reasoning implies heavy lifting)
        latency_sensitive = True
        if complexity_metrics["reasoning_depth"] == "high":
            latency_sensitive = False

        analysis = {
            "task_type": task_type,
            "complexity_score": complexity_metrics["complexity_score"],
            "estimated_tokens": complexity_metrics["estimated_tokens"],
            "latency_sensitive": latency_sensitive,
            "requires_tools": requires_tools,
            "reasoning_depth": complexity_metrics["reasoning_depth"]
        }
        
        return analysis

# Example usage
if __name__ == "__main__":
    agent = TaskAnalyzerAgent()
    print(json.dumps(agent.analyze("Design a distributed system"), indent=2))
