from agno.agent import Agent
from agno.models.openai import OpenAIChat
import os
from dotenv import load_dotenv

load_dotenv()

class CloudExecutionAgent:
    def __init__(self):
        self.api_key = os.getenv("AISA_API_KEY")
        self.base_url = "https://api.aisa.one/v1" # Assuming openai-compatible endpoint from AIsa docs
        if not self.api_key:
            raise ValueError("AISA_API_KEY not found in environment")

    def execute(self, prompt: str, model_name: str = "gpt-4o", stream: bool = True):
        """
        Executes task using AIsa.one via Agno's OpenAI integration.
        """
        try:
            # Configurable model names - AIsa usually proxies standard names
            agent = Agent(
                model=OpenAIChat(
                    id=model_name,
                    api_key=self.api_key,
                    base_url=self.base_url
                ),
                description="Cloud AI Agent",
                markdown=True
            )
            
            response = agent.run(prompt, stream=stream)
            return response
            
        except Exception as e:
            # Log error
            print(f"Cloud execution failed: {e}")
            raise e
