from fastapi.testclient import TestClient
from edgeroute.main import app
import time

import argparse

def run_demo():
    parser = argparse.ArgumentParser(description='EdgeRouteAI Demo')
    parser.add_argument('-m', '--model', type=str, help='Preferred local model (e.g. gemma3:12b)')
    args = parser.parse_args()
    
    client = TestClient(app)
    
    test_cases = [
        "Summarize this paragraph about cats.",
        "Design a distributed consensus protocol for high frequency trading.",
        "Write a regex to match email addresses.",
        "Generate a full backend architecture for a social media app with millions of users."
    ]
    
    print("🚀 Starting EdgeRouteAI Demo (via TestClient)...")
    if args.model:
        print(f"👉 Preferred Model: {args.model}")
    print("\n")
    
    for query in test_cases:
        print(f"🔹 Query: {query}")
        try:
            # Using TestClient to hit the API in-process
            payload = {"query": query}
            if args.model:
                payload["preferred_model"] = args.model
                
            response = client.post("/process", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Route: {data['route_taken'].upper()}")
                print(f"   🤖 Model: {data['model_used']}")
                print(f"   ⏱️ Time: {data['execution_time_ms']:.2f}ms")
                print(f"   📝 Reason: {data['decision_reason']}")
                # print(f"   📄 Response: {data['response'][:100]}...")
            else:
                print(f"   ❌ Error: {response.text}")
        except Exception as e:
             print(f"   ❌ Unexpected Error: {e}")
        
        print("-" * 50)
        time.sleep(1)

if __name__ == "__main__":
    run_demo()
