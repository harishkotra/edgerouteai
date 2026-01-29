from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import time
from edgeroute.agents.analyzer import TaskAnalyzerAgent
from edgeroute.agents.router import RoutingDecisionAgent
from edgeroute.agents.local import LocalExecutionAgent
from edgeroute.agents.cloud import CloudExecutionAgent
from edgeroute.agents.validator import ResponseValidatorAgent
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EdgeRouteOrchestrator")

app = FastAPI(title="EdgeRouteAI Orchestrator")

# Initialize Agents
analyzer = TaskAnalyzerAgent()
router = RoutingDecisionAgent()
local_exec = LocalExecutionAgent()
cloud_exec = CloudExecutionAgent()
validator = ResponseValidatorAgent()

class ProcessRequest(BaseModel):
    query: str
    preferred_model: Optional[str] = None

class ProcessResponse(BaseModel):
    query: str
    response: str
    route_taken: str
    model_used: str
    decision_reason: str
    execution_time_ms: float

@app.post("/process", response_model=ProcessResponse)
async def process_task(request: ProcessRequest):
    start_time = time.time()
    query = request.query
    preferred_model = request.preferred_model
    
    logger.info(f"Received query: {query}")
    
    # 1. Analyze Task
    analysis = analyzer.analyze(query)
    logger.info(f"Analysis: {analysis}")
    
    # 2. DECIDE ROUTE
    decision = router.decide(analysis, preferred_model=preferred_model)
    logger.info(f"Routing Decision: {decision}")
    
    route = decision.route
    model = decision.model
    response_content = ""
    
    # 3. EXECUTE
    try:
        if route == "local":
            try:
                # Assuming 'local_exec.execute' returns an Agno response object or generator
                # For simplicity here, we'll consume the generator if it is one, or get string
                run_response = local_exec.execute(query, model_name=model, stream=False)
                # Extract content from Agno RunResponse if needed
                response_content = getattr(run_response, "content", str(run_response))
            except Exception as e:
                logger.error(f"Local execution failed: {e}. Fallback to cloud? {decision.fallback}")
                if decision.fallback == "cloud":
                    logger.info("Falling back to Cloud...")
                    route = "cloud"
                    model = "gpt-4o" # Fallback model
                    run_response = cloud_exec.execute(query, model_name=model, stream=False)
                    response_content = getattr(run_response, "content", str(run_response))
                else:
                    raise HTTPException(status_code=500, detail=str(e))
        
        elif route == "cloud":
            run_response = cloud_exec.execute(query, model_name=model, stream=False)
            response_content = getattr(run_response, "content", str(run_response))
            
    except Exception as e:
         logger.error(f"Execution error: {e}")
         raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

    # 4. VALIDATE
    validation = validator.validate(query, response_content, source=route)
    if not validation.is_valid and validation.retry_needed and route == "local":
        logger.info(f"Validation failed ({validation.reason}). Retrying on Cloud...")
        # Retry on cloud
        route = "cloud_retry"
        model = "gpt-4o"
        try:
             run_response = cloud_exec.execute(query, model_name=model, stream=False)
             response_content = getattr(run_response, "content", str(run_response))
        except Exception as e:
             logger.error(f"Cloud retry failed: {e}")

    end_time = time.time()
    execution_time = (end_time - start_time) * 1000
    
    return ProcessResponse(
        query=query,
        response=response_content,
        route_taken=route,
        model_used=model,
        decision_reason=decision.reason,
        execution_time_ms=execution_time
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
