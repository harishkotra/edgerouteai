from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.utils.log import logger
import requests
import json
import time

class LocalExecutionAgent:
    def __init__(self):
        pass

    def execute(self, prompt: str, model_name: str, stream: bool = True):
        """
        Executes the task using Ollama via Agno or direct API.
        Using Agno's Ollama model integration is preferred if simple.
        But prompt asked for "Must implement timeout control, streaming support, etc"
        Let's use Agno Agent with Ollama model.
        """
        try:
            agent = Agent(
                model=Ollama(id=model_name),
                description="Local Edge Agent",
                markdown=True
            )
            
            logger.info(f"Starting local execution with model {model_name}")
            
            # Simple retry logic
            response = None
            try:
                response = agent.run(prompt, stream=stream)
            except Exception as e:
                logger.warning(f"Optimization: Retrying local execution once due to: {e}")
                time.sleep(1)
                response = agent.run(prompt, stream=stream)
            
            return response

        except Exception as e:
            logger.error(f"Local execution failed: {e}")
            raise e

    def execute_raw(self, prompt: str, model_name: str):
         # Direct API implementation if Agno doesn't expose timeout/fine-grained control easily
         url = "http://localhost:11434/api/generate"
         payload = {
             "model": model_name,
             "prompt": prompt,
             "stream": False
         }
         try:
             resp = requests.post(url, json=payload, timeout=30)
             resp.raise_for_status()
             return resp.json().get("response", "")
         except Exception as e:
             raise e
